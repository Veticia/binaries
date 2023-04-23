#!/bin/bash
if ! command -v bc &> /dev/null; then
    echo "Error: bc command not found. Please install bc and try again." >&2
    exit 1
fi

# Get the directory path of the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Construct the relative paths to the directories
BANNERS_DIR="$SCRIPT_DIR/banners"
ICONS_DIR="$SCRIPT_DIR/icons"
TENALDO_SQUARE_DIR="$SCRIPT_DIR/tenaldo_square"
cols=$(tput cols)

# Function to get the last part of a path and pad it with spaces
get_padded_name() {
    local path="$1"

    # Get the last part of the path after the last / character
    local name="${path##*/}"

    # Pad name with spaces up to a width of 14 characters
    local padded_name=$(printf "%-14s" "$name")

    # Return the padded name
    echo "$padded_name"
}

# Function to check if a pixel is fully opaque
is_not_transparent() {
	# Unlike in bools only return 0 is good, everything else are errors
    local pixel="$1"
    local alpha="${pixel##*,}"
    alpha="${alpha%)}"

    # Check if alpha is a valid number
    if [[ "$alpha" =~ ^[0-9]+(\.[0-9]+)?$ ]]; then
        if [[ "$alpha" == *.* || "$alpha" == "1" ]]; then
            if (( $(echo "$alpha >= 0.99" | bc -l) )); then
                return 0
            else
                return 1
            fi
        else
            if (( alpha >= 254 )); then
                return 0
            else
                return 1
            fi
        fi
    else
        # Alpha is not a valid number, abort
        return 2
    fi
}

# Function to strip alpha channel from files that are not already webp
# arguments:
#	dir
strip_alpha() {
	padded_name=$(get_padded_name "$1")
    find "$1" -type f -name "*.png" | while read file;
    do
        format=$(identify -ping -format "%m" "$file")
        # If file is WEBP it means we most likely already processed it
        if [ "$format" != "WEBP" ]; then
        	# Check if file has alpha channel at all
            if identify -ping -format '%[channels]' "$file" | grep -q 'a'; then
                # Get the dimensions of the image
                dimensions=$(identify -ping -format "%wx%h" "$file")
                width=${dimensions%x*}
                height=${dimensions#*x}

                # Get the pixels in the four corners of the image in a single command
                # Check 2 pixels from the edge to account for weird image cropping
                pixels=$(convert "$file" -format "%[pixel:p{1,1}] %[pixel:p{$((width-2)),1}] %[pixel:p{1,$((height-2))}] %[pixel:p{$((width-2)),$((height-2))}]" info:)
                read -r top_left top_right bottom_left bottom_right <<< "$pixels"

                # Check if all four corner pixels are transparent or semi-transparent
                if is_not_transparent "$top_left" && is_not_transparent "$top_right" && is_not_transparent "$bottom_left" && is_not_transparent "$bottom_right"; then
                	printf "%-${cols}s\r"
                	echo "stripping alpha       $padded_name $file"
                    convert "$file" -background black -alpha remove -alpha off "$file" &
                else
                	printf "%-${cols}s\r"
                	echo "transparent pixels in $padded_name $file"
                	# echo "            $pixels"
                fi
            else
            	    printf "%-${cols}s\r" "no transparency in    $padded_name $file"
            fi
        else
        	        printf "%-${cols}s\r" "already processed     $padded_name $file"
        fi
    done
}

# Function to reconvert and rescale images that are bigger than 1MB (and not already webp)
# arguments:
#	dir
#	target width
#	target height
#	source width  (resize if wider  than this)
#	source height (resize if taller than this)
reconvert_rescale() {
    padded_name=$(get_padded_name "$1")
    find "$1" -type f -name "*.png" -size +1M | while read file; 
    do
        format=$(identify -ping -format "%m" "$file")
        if [ "$format" != "WEBP" ]; then
            dimensions=$(identify -ping -format "%wx%h" "$file")
            width=${dimensions%x*}
            height=${dimensions#*x}
            if [ $width -gt $4 ] || [ $height -gt $5 ]; then
                printf "%-${cols}s\r"
                echo "webp'ing and resizing $padded_name $file"
                (convert "$file" -resize "${2}x${3}>" "${file%.*}.webp" && mv "${file%.*}.webp" "${file%.*}.png") &
            else
                printf "%-${cols}s\r"
                echo "webp'ing              $padded_name $file"
                (convert "$file" "${file%.*}.webp"  && mv "${file%.*}.webp" "${file%.*}.png") &
            fi
        else
            printf "%-${cols}s\r" "already processed     $padded_name $file"
        fi
    done;
}

cd "$BANNERS_DIR"
strip_alpha "$BANNERS_DIR"
reconvert_rescale "$BANNERS_DIR" 1920 1080 1920 1080

cd "$ICONS_DIR"
strip_alpha "$ICONS_DIR"
reconvert_rescale "$ICONS_DIR" 1024 1024 1080 1080

cd "$TENALDO_SQUARE_DIR"
strip_alpha "$TENALDO_SQUARE_DIR" # We shouldn't need to do that but let's check anyway
reconvert_rescale "$TENALDO_SQUARE_DIR" 1024 1024 1134 1134