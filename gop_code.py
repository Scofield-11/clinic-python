import os

# Tên file kết quả
OUTPUT_FILE = 'toan_bo_project.txt'

# Các đuôi file cần lấy code
EXTENSIONS = {'.py', '.html', '.css', '.sql', '.js'}

# Thư mục cần bỏ qua
IGNORE_DIRS = {'__pycache__', 'venv', '.git', '.idea', 'static/images'}

def merge_files():
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as outfile:
        # Duyệt qua tất cả thư mục và file
        for root, dirs, files in os.walk("."):
            # Lọc bỏ các thư mục không cần thiết
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            
            for file in files:
                # Kiểm tra đuôi file
                ext = os.path.splitext(file)[1]
                if ext in EXTENSIONS and file != os.path.basename(__file__):
                    file_path = os.path.join(root, file)
                    
                    # Ghi tên file làm tiêu đề
                    outfile.write(f"\n{'='*20}\n")
                    outfile.write(f"FILE: {file_path}\n")
                    outfile.write(f"{'='*20}\n")
                    
                    # Ghi nội dung file
                    try:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            outfile.write(infile.read())
                    except Exception as e:
                        outfile.write(f"Error reading file: {e}")
                    outfile.write("\n")
    
    print(f"Đã gộp xong! Hãy upload file '{OUTPUT_FILE}' lên Gemini.")

if __name__ == "__main__":
    merge_files()