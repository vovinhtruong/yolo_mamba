# AGENTS.md — Ngữ cảnh chung cho mọi agent

> Mọi agent (Claude, Antigravity, Gemini, Copilot, ChatGPT, Cursor) **đọc file này trước khi làm bất cứ việc gì**.
> Chỉ phó nhóm (Claude) sửa file này, và chỉ sau khi trưởng nhóm duyệt.

## 1. Đề tài
- Luận văn thạc sĩ (NTPU, SHAIL Lab) của **Vo Vinh Truong**: phát hiện gãy xương cổ tay trẻ em trên X-ray.
- Dataset chính: **GRAZPEDWRI-DX**, 1 lớp `fracture`, chia theo bệnh nhân 70/20/10 (seed 42).
- Baseline: **YOLO26** (Ultralytics 8.4.127), `imgsz=640`.
- Hai đóng góp chính:
  1. **Tích hợp Mamba (SSM) vào YOLO26** → YOLO-Mamba.
  2. **Hướng B — phương pháp xử lý input rescaling**: giữ thông tin khi ảnh X-ray có độ phân giải gốc khác nhau bị thu về 640.

## 2. Quyết định ĐÃ CHỐT — không tự ý thay đổi
- Input size mục tiêu của thí nghiệm chính: `imgsz=640`. (`1120` thuộc Hướng A, chỉ là đối chứng nếu trưởng nhóm quyết định.)
- Ablation **2 × 2** ở `imgsz=640`: {có/không rescaling B} × {có/không Mamba}.
- Không ablation so sánh nhiều vị trí Mamba: trưởng nhóm sẽ chọn **một** vị trí.
- Model dùng 4 loại khối: MLP, CNN, Attention, SSM — không dùng RNN.
- Thống kê: 3 random seeds; không dùng Wilcoxon trong proposal hiện tại.
- Hướng B là đóng góp chính; trong Proposal v2 chỉ trình bày là đóng góp chính ở chương Methodology.

## 3. CHƯA CHỐT — agent không được tự quyết, chỉ được đề xuất kèm lý do
- Vị trí đặt Mamba trong YOLO26 (ứng viên: layer 2, 4, 6, 8, 10, 13, 16, 19, 22 — xem `05_Notes/261013.md` §1).
- Thuật toán cụ thể của Hướng B.
- Epoch/batch và máy chạy cho bước train đầy đủ Mamba-YOLO-T.

## 4. Trạng thái hiện tại (cập nhật 14/10/2026)
- Baseline YOLO26 n/s/m/l/x: đã train xong (50 epoch, `imgsz=640`).
- Chạy lại paper tham khảo **Mamba-YOLO** (#11) trên máy lab: env + kernel OK, đang train thử 2 epoch.
- Đang viết **Proposal v2** (`07_Thesis/Proposal/`).
- Chi tiết mới nhất luôn nằm ở file ghi chú mới nhất trong `05_Notes/`.

## 5. Cấu trúc thư mục
**Máy Windows của trưởng nhóm** — `Desktop\yolo_mamba\`:
```
01_Papers/    paper theo nhóm (A, Basic Models, CNN-VIT, Dataset, Mamba, ...) + Summary.xlsx
02_Dataset/   GRAZ, FracAtlas, MURA (không đưa vào git)
03_Code/      ← repo git này (github.com/vovinhtruong/yolo_mamba, private)
04_Results/   bảng kết quả xlsx, biểu đồ
05_Notes/     ghi chú tiến độ (YYMMDD.md); bản cũ trong archive/
06_Reports/   slide báo cáo tuần
07_Thesis/    Thesis, Draft/, Proposal/
08_Teaching/  slide dạy sinh viên mới
```
**Repo này (`03_Code/`)**:
```
scripts/      train/eval/phân tích (đường dẫn trỏ tới máy lab ~/VINH_TRUONG/yolo26/)
env_backup/   environment.yml, requirements của env yolo26
repos/        (bị .gitignore) mã nguồn bên thứ ba: ultralytics, mamba, yolo26
```
**Máy lab (`lps_phuong`)**:
```
~/VINH_TRUONG/yolo26/            baseline, dataset/graz, runs/
~/VINH_TRUONG/yolo_mamba/        (chưa xác nhận nội dung — trưởng nhóm bổ sung)
~/VINH_TRUONG/mamba_yolo_ref/<TênBài>/env_<TênBài>/   mỗi paper tham khảo một thư mục + env riêng
```

## 6. Máy tính toán
- `lps_phuong`: 1 × RTX 3080 (~7.9 GB trống), qua Cloudflare Tunnel. Máy chính.
- `fa_server`: 4 × A40 (48 GB), đi qua `lps_phuong`. Máy mượn — **kiểm tra GPU/ổ đĩa trước khi chạy**.
- Train chạy trong **tmux**; eval/val/script khác chạy thẳng trong terminal.
- **Không ghi mật khẩu, IP, token vào repo hay bất kỳ file nào trong dự án.**

## 7. Vai trò
| Agent | Vai trò | Được làm |
|---|---|---|
| Trưởng nhóm (người) | Quyết định mọi thứ, merge vào `main` | Tất cả |
| **Claude** | Phó nhóm: điều phối, kiến trúc model, thiết kế thí nghiệm, phân tích, viết proposal/paper | Sửa `AGENTS.md`, code model (cùng trưởng nhóm) |
| Antigravity | Chạy lại paper tham khảo (dựng env, sửa lỗi, train thử) | Chỉ trong `mamba_yolo_ref/<TênBài>/` |
| Cursor | IDE chính: sửa code, refactor | Branch riêng |
| Copilot | Review PR trên GitHub | Comment, không tự push |
| Gemini | Đọc nhiều paper, related work, kiểm tra trích dẫn | Chỉ tài liệu, không sửa code |
| ChatGPT | Phản biện ý tưởng/câu chữ, soạn tài liệu dạy | Chỉ tài liệu, không sửa code |

## 8. Quy tắc làm việc
1. **Không làm gì khi trưởng nhóm chưa cho phép.** Được phản biện khi thấy vấn đề thật hoặc cách tốt hơn — luôn kèm lý do.
2. **Không bịa số liệu/bằng chứng.** Số liệu phải chỉ được về file gốc (`runs/.../results.csv`, log). Không chắc thì nói rõ; thông tin bên ngoài phải ghi nguồn.
3. Ngắn gọn, đúng trọng tâm, làm từng bước, không làm vượt phạm vi được giao.
4. **Git:** mỗi agent làm trên branch `<agent>/<việc>` (vd. `cursor/fix-eval`), mở PR → review chéo → trưởng nhóm merge. Không push thẳng vào `main`.
5. Không commit dataset, weights (`*.pt`), `runs/`, file zip.
6. Chỉ ghi vào `05_Notes/` khi trưởng nhóm yêu cầu; ghi sao cho một agent khác đọc vào là hiểu đã làm gì.
7. Phân biệt rõ **kết quả thật** và **kết quả kỳ vọng** khi viết proposal/paper.
