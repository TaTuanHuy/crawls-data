#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Run crawler
python tototuantu_main.py --category "$1" --start_page "$2" --end_page "$3" --filter "$4" --output "$5"

#!/bin/bash

# Activate virtual environment
# source venv/bin/activate

# # Cài đặt thư viện openpyxl nếu chưa có
# pip install openpyxl

# # Example using with command
#./crawl_tototuantu.sh "bon-cau" 1 1 "filter=((collectionid:product=1004146889))"

# # Run crawler
# python tototuantu_excel_main.py --category "$1" --start_page "$2" --end_page "$3" --filter "$4" --output "$5" $6


# Tham số:
# $1: Danh mục (category)
# $2: Trang bắt đầu (start_page)
# $3: Trang kết thúc (end_page)
# $4: Filter parameter
# $5: Tên file output
# $6: Tùy chọn --no_details (nếu không muốn crawl chi tiết)