symlink=$(find $1 -type l -lname '*' | grep -q . && echo true || echo false)

# files=$(ls -p "$1" | grep -v /)

files=()

# Store files in the directory in the array
for file in "$1"/*; do
    if [ -f "$file" ]; then
        files+=("$file")
    fi
done

if $symlink; then
    for ((i = 0; i < ${#files[@]}; i++)); do
        file="${files[$i]}"
        file_path="$1/$file"
        if [ -L "$file_path" ]; then
            true
            # echo "$file_path is a symbolic link. Keeping it in the array."
        else
            # echo "Removing $file from the array."
            unset 'files[i]'
        fi
    done
fi

for file in "${files[@]}"; do
    echo $file
done