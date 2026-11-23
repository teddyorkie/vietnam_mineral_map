-- Cơ sở dữ liệu Khoáng sản Việt Nam (34 Tỉnh/Thành phố mới sau sáp nhập 2025)
-- Chuẩn MySQL 8.0+ (utf8mb4) phục vụ ứng dụng bản đồ Python

CREATE DATABASE IF NOT EXISTS khoang_san_vn
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE khoang_san_vn;

DROP TABLE IF EXISTS provincial_mineral_records;
DROP TABLE IF EXISTS national_production;
DROP TABLE IF EXISTS minerals;
DROP TABLE IF EXISTS provinces;

CREATE TABLE provinces (
  id VARCHAR(10) PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  province_type VARCHAR(50) NOT NULL,
  merged_from VARCHAR(150) NOT NULL,
  lat DECIMAL(9, 6) NOT NULL,
  lng DECIMAL(9, 6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE minerals (
  id VARCHAR(50) PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  mineral_group VARCHAR(50) NOT NULL,
  national_reserve DECIMAL(14, 2) NULL,
  reserve_unit VARCHAR(100) NULL,
  source_url VARCHAR(500) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE national_production (
  id INT AUTO_INCREMENT PRIMARY KEY,
  mineral_id VARCHAR(50) NOT NULL,
  year INT NOT NULL,
  value DECIMAL(14, 2) NOT NULL,
  unit VARCHAR(100) NOT NULL,
  source_url VARCHAR(500) NOT NULL,
  FOREIGN KEY (mineral_id) REFERENCES minerals(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE provincial_mineral_records (
  id INT AUTO_INCREMENT PRIMARY KEY,
  province_id VARCHAR(10) NOT NULL,
  mineral_id VARCHAR(50) NOT NULL,
  metric_type ENUM('annual_production', 'design_capacity', 'licensed_capacity', 'distribution_only') NOT NULL,
  value DECIMAL(16, 2) NULL,
  unit VARCHAR(100) NULL,
  period VARCHAR(30) NOT NULL,
  key_mines VARCHAR(255) NOT NULL,
  notes TEXT NULL,
  source_url VARCHAR(500) NOT NULL,
  FOREIGN KEY (province_id) REFERENCES provinces(id),
  FOREIGN KEY (mineral_id) REFERENCES minerals(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO provinces (id, name, province_type, merged_from, lat, lng) VALUES
('01', 'Thành phố Hà Nội', 'Thành phố trực thuộc TW', 'Giữ nguyên (Hà Nội)', 21.028500, 105.854200),
('46', 'Thành phố Huế', 'Thành phố trực thuộc TW', 'Giữ nguyên (Huế)', 16.463700, 107.590900),
('04', 'Tỉnh Cao Bằng', 'Tỉnh', 'Giữ nguyên (Cao Bằng)', 22.666300, 106.252200),
('11', 'Tỉnh Điện Biên', 'Tỉnh', 'Giữ nguyên (Điện Biên)', 21.386000, 103.023000),
('42', 'Tỉnh Hà Tĩnh', 'Tỉnh', 'Giữ nguyên (Hà Tĩnh)', 18.355900, 105.887700),
('12', 'Tỉnh Lai Châu', 'Tỉnh', 'Giữ nguyên (Lai Châu)', 22.386200, 103.470300),
('20', 'Tỉnh Lạng Sơn', 'Tỉnh', 'Giữ nguyên (Lạng Sơn)', 21.853700, 106.761500),
('40', 'Tỉnh Nghệ An', 'Tỉnh', 'Giữ nguyên (Nghệ An)', 18.679600, 105.681300),
('22', 'Tỉnh Quảng Ninh', 'Tỉnh', 'Giữ nguyên (Quảng Ninh)', 21.006400, 107.292500),
('14', 'Tỉnh Sơn La', 'Tỉnh', 'Giữ nguyên (Sơn La)', 21.325600, 103.918800),
('38', 'Tỉnh Thanh Hóa', 'Tỉnh', 'Giữ nguyên (Thanh Hóa)', 19.806700, 105.785200),
('08', 'Tỉnh Tuyên Quang', 'Tỉnh', 'Tuyên Quang + Hà Giang', 21.823300, 105.214200),
('10', 'Tỉnh Lào Cai', 'Tỉnh', 'Lào Cai + Yên Bái', 22.480900, 103.975500),
('19', 'Tỉnh Thái Nguyên', 'Tỉnh', 'Thái Nguyên + Bắc Kạn', 21.567200, 105.825200),
('25', 'Tỉnh Phú Thọ', 'Tỉnh', 'Phú Thọ + Vĩnh Phúc + Hòa Bình', 21.322700, 105.402000),
('27', 'Tỉnh Bắc Ninh', 'Tỉnh', 'Bắc Ninh + Bắc Giang', 21.186100, 106.076300),
('33', 'Tỉnh Hưng Yên', 'Tỉnh', 'Hưng Yên + Thái Bình', 20.646400, 106.051100),
('31', 'Thành phố Hải Phòng', 'Thành phố trực thuộc TW', 'Hải Phòng + Hải Dương', 20.844900, 106.688100),
('37', 'Tỉnh Ninh Bình', 'Tỉnh', 'Ninh Bình + Hà Nam + Nam Định', 20.250600, 105.974500),
('45', 'Tỉnh Quảng Trị', 'Tỉnh', 'Quảng Trị + Quảng Bình', 16.816300, 107.100300),
('48', 'Thành phố Đà Nẵng', 'Thành phố trực thuộc TW', 'Đà Nẵng + Quảng Nam', 16.054400, 108.202200),
('51', 'Tỉnh Quảng Ngãi', 'Tỉnh', 'Quảng Ngãi + Kon Tum', 15.121400, 108.804400),
('64', 'Tỉnh Gia Lai', 'Tỉnh', 'Gia Lai + Bình Định', 13.983300, 108.000000),
('56', 'Tỉnh Khánh Hòa', 'Tỉnh', 'Khánh Hòa + Ninh Thuận', 12.258500, 109.052600),
('68', 'Tỉnh Lâm Đồng', 'Tỉnh', 'Lâm Đồng + Đắk Nông + Bình Thuận', 11.940400, 108.458300),
('66', 'Tỉnh Đắk Lắk', 'Tỉnh', 'Đắk Lắk + Phú Yên', 12.666700, 108.050000),
('79', 'Thành phố Hồ Chí Minh', 'Thành phố trực thuộc TW', 'TP.HCM + Bình Dương + Bà Rịa - Vũng Tàu', 10.776900, 106.700900),
('75', 'Tỉnh Đồng Nai', 'Tỉnh', 'Đồng Nai + Bình Phước', 10.957400, 106.842700),
('72', 'Tỉnh Tây Ninh', 'Tỉnh', 'Tây Ninh + Long An', 11.335200, 106.109900),
('92', 'Thành phố Cần Thơ', 'Thành phố trực thuộc TW', 'Cần Thơ + Sóc Trăng + Hậu Giang', 10.045200, 105.746900),
('86', 'Tỉnh Vĩnh Long', 'Tỉnh', 'Vĩnh Long + Bến Tre + Trà Vinh', 10.253700, 105.972200),
('87', 'Tỉnh Đồng Tháp', 'Tỉnh', 'Đồng Tháp + Tiền Giang', 10.493800, 105.688200),
('96', 'Tỉnh Cà Mau', 'Tỉnh', 'Cà Mau + Bạc Liêu', 9.152700, 105.196100),
('89', 'Tỉnh An Giang', 'Tỉnh', 'An Giang + Kiên Giang', 10.521600, 105.125900);

INSERT INTO minerals (id, name, mineral_group, national_reserve, reserve_unit, source_url) VALUES
('than_da', 'Than đá', 'Năng lượng', 7000.00, 'triệu tấn', 'https://vietjack.com/dia-li-8-kn/ly-thuyet-bai-3-khoang-san-viet-nam.jsp'),
('dau_mo', 'Dầu mỏ', 'Năng lượng', 10000.00, 'triệu tấn dầu quy đổi (cùng khí tự nhiên)', 'https://vietjack.com/dia-li-8-kn/ly-thuyet-bai-3-khoang-san-viet-nam.jsp'),
('khi_tu_nhien', 'Khí tự nhiên', 'Năng lượng', 432.00, 'tỉ m3 (cấp 2P)', 'https://pgs.com.vn/vi/khai-thac-su-dung-dau-mo-va-khi-thien-nhien-o-viet-nam'),
('bo_xit', 'Bô-xít (Alumin)', 'Kim loại', 9600.00, 'triệu tấn', 'https://vietjack.com/dia-li-8-kn/ly-thuyet-bai-3-khoang-san-viet-nam.jsp'),
('sat', 'Quặng sắt', 'Kim loại', 1100.00, 'triệu tấn', 'https://vietjack.com/dia-li-8-kn/ly-thuyet-bai-3-khoang-san-viet-nam.jsp'),
('ti_tan', 'Ti-tan', 'Kim loại', 663.00, 'triệu tấn', 'https://vietjack.com/dia-li-8-kn/ly-thuyet-bai-3-khoang-san-viet-nam.jsp'),
('vonfram', 'Vonfram (đa kim)', 'Kim loại', NULL, NULL, 'https://masanhightechmaterials.com/vi/subsidiary/nui-phao-mining-company/'),
('crom', 'Crôm', 'Kim loại', NULL, NULL, 'https://vietjack.com/dia-li-8-kn/ly-thuyet-bai-3-khoang-san-viet-nam.jsp'),
('thiec', 'Thiếc', 'Kim loại', NULL, NULL, 'https://vietjack.com/dia-li-8-kn/ly-thuyet-bai-3-khoang-san-viet-nam.jsp'),
('dat_hiem', 'Đất hiếm', 'Kim loại', 3.50, 'triệu tấn', 'https://cafef.vn/35-trieu-tan-tru-luong-dat-hiem-cua-viet-nam-dung-tren-ca-my-thuc-te-phu-phang-tai-cac-dn-quan-ly-khai-thac-mo-188260518073058236.chn'),
('a_pa_tit', 'A-pa-tít', 'Phi kim loại', 2000.00, 'triệu tấn', 'https://vietjack.com/dia-li-8-kn/ly-thuyet-bai-3-khoang-san-viet-nam.jsp'),
('da_voi', 'Đá vôi', 'Phi kim loại', 8000.00, 'triệu tấn', 'https://vietjack.com/dia-li-8-kn/ly-thuyet-bai-3-khoang-san-viet-nam.jsp'),
('da_quy', 'Đá quý', 'Phi kim loại', NULL, NULL, 'https://vietjack.com/dia-li-8-kn/ly-thuyet-bai-3-khoang-san-viet-nam.jsp');

INSERT INTO national_production (mineral_id, year, value, unit, source_url) VALUES
('than_da', 2010, 44.80, 'triệu tấn (than sạch)', 'https://www.gauthmath.com/vn/solution/1815477008855319/C-u-9-1-0-i-m-Cho-b-ng-s-li-u-S-n-l-ng-khai-th-c-m-t-s-kho-ng-s-n-n-c-ta-giai-H-'),
('than_da', 2021, 48.30, 'triệu tấn (than sạch)', 'https://www.gauthmath.com/vn/solution/1815477008855319/C-u-9-1-0-i-m-Cho-b-ng-s-li-u-S-n-l-ng-khai-th-c-m-t-s-kho-ng-s-n-n-c-ta-giai-H-'),
('dau_mo', 2010, 14.70, 'triệu tấn (dầu thô)', 'https://www.gauthmath.com/vn/solution/1815477008855319/C-u-9-1-0-i-m-Cho-b-ng-s-li-u-S-n-l-ng-khai-th-c-m-t-s-kho-ng-s-n-n-c-ta-giai-H-'),
('dau_mo', 2021, 9.10, 'triệu tấn (dầu thô)', 'https://www.gauthmath.com/vn/solution/1815477008855319/C-u-9-1-0-i-m-Cho-b-ng-s-li-u-S-n-l-ng-khai-th-c-m-t-s-kho-ng-s-n-n-c-ta-giai-H-'),
('khi_tu_nhien', 2010, 9.40, 'tỉ m3', 'https://www.gauthmath.com/vn/solution/1815477008855319/C-u-9-1-0-i-m-Cho-b-ng-s-li-u-S-n-l-ng-khai-th-c-m-t-s-kho-ng-s-n-n-c-ta-giai-H-'),
('khi_tu_nhien', 2021, 7.40, 'tỉ m3', 'https://www.gauthmath.com/vn/solution/1815477008855319/C-u-9-1-0-i-m-Cho-b-ng-s-li-u-S-n-l-ng-khai-th-c-m-t-s-kho-ng-s-n-n-c-ta-giai-H-');

INSERT INTO provincial_mineral_records (province_id, mineral_id, metric_type, value, unit, period, key_mines, notes, source_url) VALUES
('22', 'than_da', 'annual_production', 38.10, 'triệu tấn (than sạch TKV)', '2024', 'Bể than Quảng Ninh (Hà Tu, Hạ Long, Uông Bí, Cẩm Phả)', 'Tỉnh giữ nguyên sau sáp nhập; trữ lượng antraxit đạt trên 3 tỉ tấn.', 'https://www.quangninh.gov.vn/Trang/ChiTietTinTuc.aspx?nid=150986'),
('22', 'than_da', 'annual_production', 38.63, 'triệu tấn (than sạch TKV)', '2025', 'Bể than Quảng Ninh', 'Sản lượng than sạch toàn Tập đoàn TKV năm 2025, tập trung chủ yếu tại Quảng Ninh.', 'https://baoquangninh.vn/mot-nam-thang-loi-cua-nganh-than-post3391846.html'),
('79', 'dau_mo', 'distribution_only', NULL, NULL, '2024-2025', 'Thềm lục địa phía Đông Nam - khu vực Bà Rịa - Vũng Tàu (Bạch Hổ, Đại Hùng, Rồng, Rạng Đông, Hồng Ngọc)', 'Gộp từ tỉnh Bà Rịa - Vũng Tàu vào TP. Hồ Chí Minh mới; sản lượng dầu thô trong nước trung bình 7,5 - 8,5 triệu tấn/năm.', 'https://pgs.com.vn/vi/khai-thac-su-dung-dau-mo-va-khi-thien-nhien-o-viet-nam'),
('79', 'khi_tu_nhien', 'distribution_only', NULL, NULL, '2024-2025', 'Bể Cửu Long, Nam Côn Sơn (khu vực Bà Rịa - Vũng Tàu)', 'Gộp từ tỉnh Bà Rịa - Vũng Tàu vào TP. Hồ Chí Minh mới; nguồn cung cấp khí tự nhiên chủ lực của cả nước.', 'https://pgs.com.vn/vi/khai-thac-su-dung-dau-mo-va-khi-thien-nhien-o-viet-nam'),
('68', 'bo_xit', 'design_capacity', 1300000.00, 'tấn alumin/năm (gộp 2 tổ hợp Tân Rai & Nhân Cơ)', '2024-2025', 'Tổ hợp bô-xít - nhôm Tân Rai (650.000 tấn/năm) & Tổ hợp alumin Nhân Cơ (650.000 tấn/năm)', 'Gộp từ Lâm Đồng + Đắk Nông + Bình Thuận thành tỉnh Lâm Đồng mới (trung tâm bô-xít - nhôm lớn nhất Việt Nam; lũy kế Tân Rai 7,47 triệu tấn & Nhân Cơ 5,47 triệu tấn alumin quy đổi đến 2024).', 'https://baolamdong.vn/to-hop-alumin-nhan-co-tan-rai-hat-nhan-thuc-day-trung-tam-nhom-quoc-gia-250881.html'),
('68', 'ti_tan', 'distribution_only', NULL, NULL, '2024-2025', 'Ven biển khu vực Bình Thuận', 'Gộp từ tỉnh Bình Thuận vào tỉnh Lâm Đồng mới; khai thác ti-tan và cát thủy tinh ven biển.', 'https://vietjack.com/dia-li-8-kn/ly-thuyet-bai-3-khoang-san-viet-nam.jsp'),
('10', 'a_pa_tit', 'licensed_capacity', 3100000.00, 'tấn quặng/năm', '2023-2025', 'Mỏ Apatit Lào Cai (hữu ngạn sông Hồng)', 'Gộp Lào Cai + Yên Bái thành tỉnh Lào Cai mới; mỏ Apatit duy nhất tại Việt Nam (kế hoạch 2026: 1,99 triệu tấn).', 'https://www.vinachem.com.vn/nd/tin-tap-doan/tiep-tuc-thao-go-kho-khan-vuong-mac-cho-cong-ty-apatit-viet-nam.html'),
('10', 'sat', 'distribution_only', NULL, NULL, '2024-2025', 'Các mỏ sắt khu vực Lào Cai', 'Thuộc tỉnh Lào Cai mới (Lào Cai + Yên Bái).', 'https://vietjack.com/dia-li-8-kn/ly-thuyet-bai-3-khoang-san-viet-nam.jsp'),
('19', 'vonfram', 'distribution_only', NULL, NULL, '2024-2025', 'Mỏ đa kim Núi Pháo', 'Gộp Thái Nguyên + Bắc Kạn thành tỉnh Thái Nguyên mới; mỏ vonfram trữ lượng lớn thứ 2 thế giới ngoài Trung Quốc.', 'https://masanhightechmaterials.com/vi/subsidiary/nui-phao-mining-company/'),
('19', 'sat', 'distribution_only', NULL, NULL, '2024-2025', 'Vùng mỏ Đông Bắc - Thái Nguyên', 'Mỏ sắt và ti-tan quy mô lớn thuộc tỉnh Thái Nguyên mới.', 'https://vietjack.com/dia-li-8-kn/ly-thuyet-bai-3-khoang-san-viet-nam.jsp'),
('42', 'sat', 'distribution_only', NULL, NULL, '2024-2025', 'Vùng mỏ Bắc Trung Bộ - Hà Tĩnh', 'Tỉnh giữ nguyên sau sáp nhập; điểm tập trung quặng sắt quy mô lớn.', 'https://vietjack.com/dia-li-8-kn/ly-thuyet-bai-3-khoang-san-viet-nam.jsp'),
('38', 'crom', 'distribution_only', NULL, NULL, '2024-2025', 'Vùng mỏ Bắc Trung Bộ - Thanh Hóa', 'Tỉnh giữ nguyên sau sáp nhập; mỏ crôm quy mô lớn tại Việt Nam.', 'https://vietjack.com/dia-li-8-kn/ly-thuyet-bai-3-khoang-san-viet-nam.jsp'),
('38', 'da_voi', 'distribution_only', NULL, NULL, '2024-2025', 'Các mỏ đá vôi xi măng Thanh Hóa', 'Tỉnh giữ nguyên sau sáp nhập; thuộc vùng núi Bắc Trung Bộ tập trung đá vôi.', 'https://ximang.vn/danh-gia-tru-luong-mo-khoang-san-lam-nguyen-lieu-san-xuat-xi-mang-tai-thanh-hoa-hoa-binh-19246'),
('40', 'thiec', 'distribution_only', NULL, NULL, '2024-2025', 'Vùng mỏ Bắc Trung Bộ - Nghệ An', 'Tỉnh giữ nguyên sau sáp nhập; tập trung thiếc và đá quý quy mô lớn.', 'https://vietjack.com/dia-li-8-kn/ly-thuyet-bai-3-khoang-san-viet-nam.jsp'),
('40', 'da_quy', 'distribution_only', NULL, NULL, '2024-2025', 'Vùng mỏ Bắc Trung Bộ - Nghệ An', 'Tỉnh giữ nguyên sau sáp nhập; khai thác đá quý tại Nghệ An.', 'https://vietjack.com/dia-li-8-kn/ly-thuyet-bai-3-khoang-san-viet-nam.jsp'),
('12', 'dat_hiem', 'distribution_only', NULL, NULL, '2024-2025', 'Mỏ Đông Pao (diện tích 4 mỏ/điểm khoáng sản 2.779,4 ha)', 'Tỉnh giữ nguyên sau sáp nhập; sở hữu mỏ đất hiếm lớn nhất Việt Nam.', 'https://cafef.vn/35-trieu-tan-tru-luong-dat-hiem-cua-viet-nam-dung-tren-ca-my-thuc-te-phu-phang-tai-cac-dn-quan-ly-khai-thac-mo-188260518073058236.chn'),
('08', 'bo_xit', 'distribution_only', NULL, NULL, '2024-2025', 'Bô-xít diaspor khu vực Hà Giang', 'Gộp từ tỉnh Hà Giang vào tỉnh Tuyên Quang mới.', 'https://vietjack.com/dia-li-8-kn/ly-thuyet-bai-3-khoang-san-viet-nam.jsp'),
('04', 'bo_xit', 'distribution_only', NULL, NULL, '2024-2025', 'Bô-xít diaspor Cao Bằng', 'Tỉnh giữ nguyên sau sáp nhập; phân bố bô-xít phía Bắc.', 'https://vietjack.com/dia-li-8-kn/ly-thuyet-bai-3-khoang-san-viet-nam.jsp'),
('20', 'bo_xit', 'distribution_only', NULL, NULL, '2024-2025', 'Bô-xít diaspor Lạng Sơn', 'Tỉnh giữ nguyên sau sáp nhập; phân bố bô-xít phía Bắc.', 'https://vietjack.com/dia-li-8-kn/ly-thuyet-bai-3-khoang-san-viet-nam.jsp'),
('64', 'bo_xit', 'distribution_only', NULL, NULL, '2024-2025', 'Vùng bô-xít Tây Nguyên - khu vực Gia Lai', 'Gộp Gia Lai + Bình Định thành tỉnh Gia Lai mới.', 'https://vietjack.com/dia-li-8-kn/ly-thuyet-bai-3-khoang-san-viet-nam.jsp'),
('51', 'bo_xit', 'distribution_only', NULL, NULL, '2024-2025', 'Vùng bô-xít Tây Nguyên - khu vực Kon Tum', 'Gộp từ tỉnh Kon Tum vào tỉnh Quảng Ngãi mới.', 'https://vietjack.com/dia-li-8-kn/ly-thuyet-bai-3-khoang-san-viet-nam.jsp'),
('56', 'ti_tan', 'distribution_only', NULL, NULL, '2024-2025', 'Ven biển Khánh Hòa & khu vực Ninh Thuận', 'Gộp Khánh Hòa + Ninh Thuận thành tỉnh Khánh Hòa mới; khai thác ti-tan và cát thủy tinh ven biển.', 'https://vietjack.com/dia-li-8-kn/ly-thuyet-bai-3-khoang-san-viet-nam.jsp');