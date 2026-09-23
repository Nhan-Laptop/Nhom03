# Lab 1 – B.1 (Git): log lệnh & output thực tế

- Máy: Linux (Linux 7.1.5+kali-amd64), git 2.53.0
- Nhóm: Nhom03 | Repo local: `/home/nhanlaptop/UIT/NT521/TH1/Nhom03` (repo root = Nhom03, tương ứng `git-intro` trong PDF)
- Ghi chú layout: PDF mô tả `mkdir NhomX && mkdir git-intro && cd git-intro && git init`. Ở bài này repo root được đặt thẳng tại `Nhom03/` để khớp với B.1.6 (`cd ~/NhomXX` + `git push -u origin master`) và B.2 (folder `unittest/`). Bước mkdir NhomX và git-intro vì vậy đã có/được gộp.
- Ngày chạy: 2026-09-23 08:29:30 +07

---

## B.1.1 Thiết lập Git Repository

### Bước 1. Cấu hình thông tin người dùng và liên kết tài khoản
$ git config --global user.name "Nhom 03"

$ git config --global user.email nguyentrongnhan06cm@gmail.com

### Bước 2. Kiểm tra lại thông tin người dùng
$ git config --list
credential.https://github.com.helper=
credential.https://github.com.helper=!/usr/bin/gh auth git-credential
credential.https://gist.github.com.helper=
credential.https://gist.github.com.helper=!/usr/bin/gh auth git-credential
user.name=Nhom 03
user.email=nguyentrongnhan06cm@gmail.com

### Bước 3–4. Tạo thư mục NhomX (đã có) và git-intro
(repo root của bài này là `Nhom03/`, xem ghi chú layout ở đầu file)
$ pwd
/home/nhanlaptop/UIT/NT521/TH1/Nhom03

### Bước 5. Khởi tạo Git repository + kiểm tra thư mục ẩn
$ git init
hint: Using 'master' as the name for the initial branch. This default branch name
hint: will change to "main" in Git 3.0. To configure the initial branch name
hint: to use in all of your new repositories, which will suppress this warning,
hint: call:
hint:
hint: 	git config --global init.defaultBranch <name>
hint:
hint: Names commonly chosen instead of 'master' are 'main', 'trunk' and
hint: 'development'. The just-created branch can be renamed via this command:
hint:
hint: 	git branch -m <name>
hint:
hint: Disable this message with "git config set advice.defaultBranchName false"
Initialized empty Git repository in /home/nhanlaptop/UIT/NT521/TH1/Nhom03/.git/

$ ls -a
.
..
.git
.pi

### Bước 6. Xem trạng thái repository cục bộ
$ git status
On branch master

No commits yet

nothing to commit (create/copy files and use "git add" to track)

---

## B.1.2 Staging và Committing một tập tin lên Repository

### Bước 1. Tạo tập tin README.MD (tên nhóm + danh sách thành viên)
$ cat > README.MD <<'EOF'
# Nhom03
Nguyen Trong Nhan - 24521236
Nguyen Trong Nhan - 24520023
Le Viet Hoang - 24520546
EOF

### Bước 2. Kiểm tra tập tin vừa tạo
$ ls -la
total 20
drwxrwxr-x 4 nhanlaptop nhanlaptop 4096 Sep 23 08:29 .
drwxrwxr-x 6 nhanlaptop nhanlaptop 4096 Sep 23 08:29 ..
drwxrwxr-x 6 nhanlaptop nhanlaptop 4096 Sep 23 08:29 .git
drwxrwxr-x 3 nhanlaptop nhanlaptop 4096 Sep 23 08:21 .pi
-rw-rw-r-- 1 nhanlaptop nhanlaptop   92 Sep 23 08:29 README.MD

$ cat README.MD
# Nhom03
Nguyen Trong Nhan - 24521236
Nguyen Trong Nhan - 24520023
Le Viet Hoang - 24520546

### Bước 3. Kiểm tra trạng thái repository sau khi tạo tập tin
$ git status
On branch master

No commits yet

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	README.MD

nothing added to commit but untracked files present (use "git add" to track)

### Bước 4. Staging tập tin (đưa vào vùng staging)
$ git add README.MD

### Bước 5. Kiểm tra trạng thái repository sau khi stage
$ git status
On branch master

No commits yet

Changes to be committed:
  (use "git rm --cached <file>..." to unstage)
	new file:   README.MD


### Bước 6. Commit tập tin
$ git commit -m "Committing README.MD from Nhom03 to begin tracking changes"
[master (root-commit) 6b0c49e] Committing README.MD from Nhom03 to begin tracking changes
 1 file changed, 4 insertions(+)
 create mode 100644 README.MD

### Bước 7. Xem lịch sử commit
$ git log
commit 6b0c49e3ee6e89d71551ac2c1557aeefd6978f08
Author: Nhom 03 <nguyentrongnhan06cm@gmail.com>
Date:   Wed Sep 23 08:29:34 2026 +0700

    Committing README.MD from Nhom03 to begin tracking changes

---

## B.1.3 Sửa đổi tập tin và theo dõi các thay đổi

### Bước 1. Chèn thêm 1 dòng vào cuối tập tin README.MD
$ echo "I am beginning to understand Git" >> README.MD

### Bước 2. Xem lại nội dung tập tin đã chỉnh sửa
$ cat README.MD
# Nhom03
Nguyen Trong Nhan - 24521236
Nguyen Trong Nhan - 24520023
Le Viet Hoang - 24520546
I am beginning to understand Git

### Bước 3. Kiểm tra thay đổi đối với repository
$ git status
On branch master
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   README.MD

no changes added to commit (use "git add" and/or "git commit -a")

### Bước 4. Stage và commit tập tin đã thay đổi
$ git add README.MD

$ git commit -m "Nhom03 Added additional line to file"
[master b889aa8] Nhom03 Added additional line to file
 1 file changed, 1 insertion(+)

### Bước 5. Xem lại commit vừa thực hiện
$ git log
commit b889aa8cdfaf0ece28b947000c2ec10f04ec90de
Author: Nhom 03 <nguyentrongnhan06cm@gmail.com>
Date:   Wed Sep 23 08:29:39 2026 +0700

    Nhom03 Added additional line to file

commit 6b0c49e3ee6e89d71551ac2c1557aeefd6978f08
Author: Nhom 03 <nguyentrongnhan06cm@gmail.com>
Date:   Wed Sep 23 08:29:34 2026 +0700

    Committing README.MD from Nhom03 to begin tracking changes

### Bước 6. So sánh 2 commit
$ git diff 6b0c49e3ee6e89d71551ac2c1557aeefd6978f08 HEAD
diff --git a/README.MD b/README.MD
index b32e865..0d2a1c2 100644
--- a/README.MD
+++ b/README.MD
@@ -2,3 +2,4 @@
 Nguyen Trong Nhan - 24521236
 Nguyen Trong Nhan - 24520023
 Le Viet Hoang - 24520546
+I am beginning to understand Git

---

## B.1.4 Branches và Merging

### a) Làm việc trong branch
#### Bước 1. Tạo branch mới tên feature
$ git branch feature

#### Bước 2. Kiểm tra branch hiện tại
$ git branch
  feature
* master

#### Bước 3. Chuyển (checkout) sang branch feature
$ git checkout feature
Switched to branch 'feature'

#### Bước 4. Kiểm tra lại branch hiện tại
$ git branch
* feature
  master

#### Bước 5. Thay đổi README.MD, stage và commit trên branch feature
$ echo "This is a new line from branch feature" >> README.MD

$ cat README.MD
# Nhom03
Nguyen Trong Nhan - 24521236
Nguyen Trong Nhan - 24520023
Le Viet Hoang - 24520546
I am beginning to understand Git
This is a new line from branch feature

$ git add README.MD

$ git status
On branch feature
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
	modified:   README.MD


$ git commit -m "Added a third line in feature branch"
[feature 6f0dc98] Added a third line in feature branch
 1 file changed, 1 insertion(+)

$ git log
commit 6f0dc98809d00cd4908f0fbd873e21b8ff1b3b28
Author: Nhom 03 <nguyentrongnhan06cm@gmail.com>
Date:   Wed Sep 23 08:29:39 2026 +0700

    Added a third line in feature branch

commit b889aa8cdfaf0ece28b947000c2ec10f04ec90de
Author: Nhom 03 <nguyentrongnhan06cm@gmail.com>
Date:   Wed Sep 23 08:29:39 2026 +0700

    Nhom03 Added additional line to file

commit 6b0c49e3ee6e89d71551ac2c1557aeefd6978f08
Author: Nhom 03 <nguyentrongnhan06cm@gmail.com>
Date:   Wed Sep 23 08:29:34 2026 +0700

    Committing README.MD from Nhom03 to begin tracking changes

### b) Merge các thay đổi từ branch feature vào branch master
#### Bước 1. Chuyển về branch master
$ git checkout master
Switched to branch 'master'

#### Bước 2. Kiểm tra README.MD ở nhánh master (feature chưa merge nên chưa có dòng mới)
$ cat README.MD
# Nhom03
Nguyen Trong Nhan - 24521236
Nguyen Trong Nhan - 24520023
Le Viet Hoang - 24520546
I am beginning to understand Git

#### Bước 3. Merge branch feature vào master
$ git merge feature
Updating b889aa8..6f0dc98
Fast-forward
 README.MD | 1 +
 1 file changed, 1 insertion(+)

#### Bước 4. Kiểm tra nội dung README.MD sau khi merge
$ cat README.MD
# Nhom03
Nguyen Trong Nhan - 24521236
Nguyen Trong Nhan - 24520023
Le Viet Hoang - 24520546
I am beginning to understand Git
This is a new line from branch feature

#### Bước 5. Xoá branch feature
$ git branch
  feature
* master

$ git branch -d feature
Deleted branch feature (was 6f0dc98).

$ git branch
* master

---

## B.1.5 Xử lý xung đột khi merge

### Bước 1. Tạo branch test mới và chuyển sang branch test
$ git branch test

$ git checkout test
Switched to branch 'test'

### Bước 2. Chỉnh sửa nội dung README.MD bằng sed
$ sed -i 's/feature/test/' README.MD
Nội dung README.MD TRƯỚC khi chạy:
$ cat README.MD
# Nhom03
Nguyen Trong Nhan - 24521236
Nguyen Trong Nhan - 24520023
Le Viet Hoang - 24520546
I am beginning to understand Git
This is a new line from branch feature

Nội dung README.MD SAU khi chạy (dòng cuối đổi 'feature' -> 'test'):
$ cat README.MD
# Nhom03
Nguyen Trong Nhan - 24521236
Nguyen Trong Nhan - 24520023
Le Viet Hoang - 24520546
I am beginning to understand Git
This is a new line from branch test

### Bước 3. Stage + commit tập tin trên branch test
$ git commit -a -m "branch test Change feature to test"
[test eda981f] branch test Change feature to test
 1 file changed, 1 insertion(+), 1 deletion(-)

### Bước 4. Chuyển sang branch master và chỉnh sửa README.MD
$ git checkout master
Switched to branch 'master'

$ sed -i 's/feature/master/' README.MD
$ cat README.MD
# Nhom03
Nguyen Trong Nhan - 24521236
Nguyen Trong Nhan - 24520023
Le Viet Hoang - 24520546
I am beginning to understand Git
This is a new line from branch master

### Bước 5. Stage + commit tập tin trên branch master
$ git commit -a -m "branch master Changed feature to master"
[master 62a858e] branch master Changed feature to master
 1 file changed, 1 insertion(+), 1 deletion(-)

### Bước 6. Merge hai branch test và master
$ git merge test
Auto-merging README.MD
CONFLICT (content): Merge conflict in README.MD
Automatic merge failed; fix conflicts and then commit the result.

-> exit status = 1 (khác 0 => merge KHÔNG tự động được vì xung đột)
### Bước 7. Xem các commit (HEAD đang ở branch master)
$ git log --decorate --oneline --graph --all
* 62a858e (HEAD -> master) branch master Changed feature to master
| * eda981f (test) branch test Change feature to test
|/  
* 6f0dc98 Added a third line in feature branch
* b889aa8 Nhom03 Added additional line to file
* 6b0c49e Committing README.MD from Nhom03 to begin tracking changes

$ git status
On branch master
You have unmerged paths.
  (fix conflicts and run "git commit")
  (use "git merge --abort" to abort the merge)

Unmerged paths:
  (use "git add <file>..." to mark resolution)
	both modified:   README.MD

no changes added to commit (use "git add" and/or "git commit -a")

### Bước 8. Tìm và xoá xung đột trong README.MD
README.MD chứa conflict marker:
$ cat README.MD
# Nhom03
Nguyen Trong Nhan - 24521236
Nguyen Trong Nhan - 24520023
Le Viet Hoang - 24520546
I am beginning to understand Git
<<<<<<< HEAD
This is a new line from branch master
=======
This is a new line from branch test
>>>>>>> test

Xoá 3 dòng marker và dòng của branch test (giữ lại dòng của branch master - HEAD):
$ sed -i -e '/^<<<<<<</d' -e '/^=======$/d' -e '/^>>>>>>>/d' -e '/from branch test$/d' README.MD
Kiểm tra kết quả sau khi xoá xung đột:
$ cat README.MD
# Nhom03
Nguyen Trong Nhan - 24521236
Nguyen Trong Nhan - 24520023
Le Viet Hoang - 24520546
I am beginning to understand Git
This is a new line from branch master

### Bước 9. Stage, commit và kiểm tra log của branch master
$ git add README.MD

$ git commit -a -m "Manually merged from test branch"
[master a6c11b2] Manually merged from test branch

$ git log
commit a6c11b2bf5d5eeb6a812d690a24be37eb082bffe
Merge: 62a858e eda981f
Author: Nhom 03 <nguyentrongnhan06cm@gmail.com>
Date:   Wed Sep 23 08:30:07 2026 +0700

    Manually merged from test branch

commit 62a858e45e2d1e686bbcacb87aaf242d7cb59f3a
Author: Nhom 03 <nguyentrongnhan06cm@gmail.com>
Date:   Wed Sep 23 08:30:07 2026 +0700

    branch master Changed feature to master

commit eda981f4b1548f59e19d34f1844625f3033ce42d
Author: Nhom 03 <nguyentrongnhan06cm@gmail.com>
Date:   Wed Sep 23 08:30:07 2026 +0700

    branch test Change feature to test

commit 6f0dc98809d00cd4908f0fbd873e21b8ff1b3b28
Author: Nhom 03 <nguyentrongnhan06cm@gmail.com>
Date:   Wed Sep 23 08:29:39 2026 +0700

    Added a third line in feature branch

commit b889aa8cdfaf0ece28b947000c2ec10f04ec90de
Author: Nhom 03 <nguyentrongnhan06cm@gmail.com>
Date:   Wed Sep 23 08:29:39 2026 +0700

    Nhom03 Added additional line to file

commit 6b0c49e3ee6e89d71551ac2c1557aeefd6978f08
Author: Nhom 03 <nguyentrongnhan06cm@gmail.com>
Date:   Wed Sep 23 08:29:34 2026 +0700

    Committing README.MD from Nhom03 to begin tracking changes

$ git branch
* master
  test

### Trạng thái cuối cùng
$ git status
On branch master
nothing to commit, working tree clean

---

## B.1.6 Tích hợp Git với GitHub

### Bước 0 (chuẩn bị). Đưa .gitignore + git-intro lên master
$ git status
On branch master
Untracked files:
  (use "git add <file>..." to include in what will be committed)
	.gitignore
	git-intro/

nothing added to commit but untracked files present (use "git add" to track)

$ cat .gitignore
# Pi agent session data (local only)
.pi/

# Lab documents -- KHONG duoc dang tai len internet
*.pdf

# OS / editor noise
.DS_Store
Thumbs.db
*.swp
*~

$ git add .gitignore git-intro

$ git commit -m "Nhom03 Add .gitignore and group intro note"
[master 777d732] Nhom03 Add .gitignore and group intro note
 2 files changed, 17 insertions(+)
 create mode 100644 .gitignore
 create mode 100644 git-intro/Readme.md

### Bước 1. Tạo Repository rỗng trên GitHub
(repo đã được tạo sẵn trên GitHub; kiểm tra lại thông tin repo)
$ gh repo view Nhan-Laptop/Nhom03 --json name,visibility,defaultBranchRef,url
{"defaultBranchRef":{"name":"master"},"name":"Nhom03","url":"https://github.com/Nhan-Laptop/Nhom03","visibility":"PUBLIC"}

### Bước 2. Xác thực tài khoản GitHub trên máy — Cách A: GitHub CLI
$ gh auth login --hostname github.com --git-protocol https --web

! One-time code (F99F-1AF7) copied to clipboard
Open this URL to continue in your web browser: https://github.com/login/device
Ghi chú: lệnh `gh auth login --web` ở trên in ra 8 ký tự one-time code và URL https://github.com/login/device rồi dừng lại chờ xác nhận trên trình duyệt. Do tài khoản đã đăng nhập sẵn (`gh auth status` bên dưới xác nhận phiên còn hiệu lực), luồng xác thực này không cần hoàn tất lại.

$ gh auth setup-git

$ gh auth status
github.com
  ✓ Logged in to github.com account Nhan-Laptop (keyring)
  - Active account: true
  - Git operations protocol: https
  - Token: gho_************************************
  - Token scopes: 'gist', 'read:org', 'repo', 'workflow'

### Bước 3. Đứng đúng repository và nhánh master
(trong máy ảo của bài lab đường dẫn là ~/Nhom03, ở đây repo nằm trong thư mục bài tập)
$ pwd
/home/nhanlaptop/UIT/NT521/TH1/Nhom03

$ git checkout master
Already on 'master'

$ git log --oneline
777d732 Nhom03 Add .gitignore and group intro note
a6c11b2 Manually merged from test branch
62a858e branch master Changed feature to master
eda981f branch test Change feature to test
6f0dc98 Added a third line in feature branch
b889aa8 Nhom03 Added additional line to file
6b0c49e Committing README.MD from Nhom03 to begin tracking changes

### Bước 4. Trỏ Git repository cục bộ đến GitHub repository
$ git remote add origin https://github.com/Nhan-Laptop/Nhom03.git

$ git remote -v
origin	https://github.com/Nhan-Laptop/Nhom03.git (fetch)
origin	https://github.com/Nhan-Laptop/Nhom03.git (push)

### Bước 5. Gửi toàn bộ mã nguồn và lịch sử lên GitHub
$ git push -u origin master --force
To https://github.com/Nhan-Laptop/Nhom03.git
 + a8afbf1...777d732 master -> master (forced update)
branch 'master' set up to track 'origin/master'.

-> exit status = 0
### Bước 6. Kiểm tra kết quả trên GitHub
$ git ls-remote origin
777d7323c2dc3c2e87377b327381229941e14956	HEAD
777d7323c2dc3c2e87377b327381229941e14956	refs/heads/master

$ gh repo view Nhan-Laptop/Nhom03 --json name,visibility,pushedAt,url
{"name":"Nhom03","pushedAt":"2026-09-23T01:36:14Z","url":"https://github.com/Nhan-Laptop/Nhom03","visibility":"PUBLIC"}

$ gh api repos/Nhan-Laptop/Nhom03/commits --jq '.[] | "\(.sha[0:7]) \(.commit.message)"'
777d732 Nhom03 Add .gitignore and group intro note
a6c11b2 Manually merged from test branch
62a858e branch master Changed feature to master
eda981f branch test Change feature to test
6f0dc98 Added a third line in feature branch
b889aa8 Nhom03 Added additional line to file
6b0c49e Committing README.MD from Nhom03 to begin tracking changes

$ gh api repos/Nhan-Laptop/Nhom03/git/trees/master --jq '.tree[].path'
.gitignore
README.MD
git-intro

$ gh api repos/Nhan-Laptop/Nhom03/contents/README.MD --jq .content | base64 -d
# Nhom03
Nguyen Trong Nhan - 24521236
Nguyen Trong Nhan - 24520023
Le Viet Hoang - 24520546
I am beginning to understand Git
This is a new line from branch master

$ git status
On branch master
Your branch is up to date with 'origin/master'.

nothing to commit, working tree clean

### Trạng thái cuối cùng của B.1
$ git log --oneline --decorate --graph --all
* 777d732 (HEAD -> master, origin/master) Nhom03 Add .gitignore and group intro note
*   a6c11b2 Manually merged from test branch
|\  
| * eda981f (test) branch test Change feature to test
* | 62a858e branch master Changed feature to master
|/  
* 6f0dc98 Added a third line in feature branch
* b889aa8 Nhom03 Added additional line to file
* 6b0c49e Committing README.MD from Nhom03 to begin tracking changes

