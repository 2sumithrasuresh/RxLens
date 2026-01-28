USE rxlens;

-- ==========================================================
-- DRUG MASTER DATA
-- ==========================================================
INSERT INTO drugs (name) VALUES
('Paracetamol'),
('Ibuprofen'),
('Amoxicillin'),
('Clavulanic Acid'),
('Cetirizine'),
('Caffeine'),
('Phenylephrine'),
('Chlorpheniramine'),
('Dextromethorphan'),
('Guaifenesin'),
('Azithromycin'),
('Pantoprazole'),
('Domperidone'),
('Vitamin C'),
('Zinc');

-- ==========================================================
-- BRAND MEDICINES
-- ==========================================================
INSERT INTO brand_medicines (brand_name, medicine_name) VALUES
('Crocin', 'Crocin Advance'),
('Calpol', 'Calpol 650'),
('Augmentin', 'Augmentin 625'),
('Vicks', 'Vicks Action 500'),
('Benadryl', 'Benadryl Cough Formula'),
('Zincovit', 'Zincovit Tablet'),
('Combiflam', 'Combiflam Tablet'),
('Pantocid', 'Pantocid DSR');

-- ==========================================================
-- BRAND MEDICINE COMPOSITIONS
-- ==========================================================

-- Crocin Advance (single drug)
INSERT INTO brand_medicine_composition VALUES
(NULL, 1, 1, 500);

-- Calpol 650 (single drug, different strength)
INSERT INTO brand_medicine_composition VALUES
(NULL, 2, 1, 650);

-- Augmentin 625 (2 drugs)
INSERT INTO brand_medicine_composition VALUES
(NULL, 3, 3, 500),
(NULL, 3, 4, 125);

-- Vicks Action 500 (4 drugs)
INSERT INTO brand_medicine_composition VALUES
(NULL, 4, 1, 500),
(NULL, 4, 6, 30),
(NULL, 4, 7, 10),
(NULL, 4, 8, 2);

-- Benadryl Cough Formula (4 drugs)
INSERT INTO brand_medicine_composition VALUES
(NULL, 5, 9, 10),
(NULL, 5, 10, 100),
(NULL, 5, 7, 5),
(NULL, 5, 8, 2);

-- Zincovit (multi-vitamin, partial match candidate)
INSERT INTO brand_medicine_composition VALUES
(NULL, 6, 14, 75),
(NULL, 6, 15, 10);

-- Combiflam (2 drugs)
INSERT INTO brand_medicine_composition VALUES
(NULL, 7, 1, 325),
(NULL, 7, 2, 400);

-- Pantocid DSR (2 drugs)
INSERT INTO brand_medicine_composition VALUES
(NULL, 8, 12, 40),
(NULL, 8, 13, 30);

-- ==========================================================
-- JAN AUSHADHI MEDICINES
-- ==========================================================
INSERT INTO jan_aushadhi_medicines (medicine_name) VALUES
('Paracetamol Tablet IP 500mg'),
('Paracetamol Tablet IP 650mg'),
('Amoxicillin + Clavulanate Tablet IP'),
('Cold Relief Tablet IP'),
('Cough Suppressant Syrup IP'),
('Vitamin C + Zinc Tablet IP'),
('Ibuprofen + Paracetamol Tablet IP'),
('Pantoprazole + Domperidone Capsule IP');

-- ==========================================================
-- JAN AUSHADHI COMPOSITIONS
-- ==========================================================

-- Exact match: Paracetamol 500
INSERT INTO jan_aushadhi_composition VALUES
(NULL, 1, 1, 500);

-- Exact match: Paracetamol 650
INSERT INTO jan_aushadhi_composition VALUES
(NULL, 2, 1, 650);

-- Exact match: Augmentin equivalent
INSERT INTO jan_aushadhi_composition VALUES
(NULL, 3, 3, 500),
(NULL, 3, 4, 125);

-- Partial match: Cold Relief (same drugs, different amounts)
INSERT INTO jan_aushadhi_composition VALUES
(NULL, 4, 1, 450),
(NULL, 4, 6, 25),
(NULL, 4, 7, 5),
(NULL, 4, 8, 2);

-- Partial match: Cough syrup (overlapping but missing drug)
INSERT INTO jan_aushadhi_composition VALUES
(NULL, 5, 9, 10),
(NULL, 5, 10, 100);

-- Partial match: Vitamin + Zinc (different ratio)
INSERT INTO jan_aushadhi_composition VALUES
(NULL, 6, 14, 60),
(NULL, 6, 15, 15);

-- Partial match: Combiflam equivalent (different ratio)
INSERT INTO jan_aushadhi_composition VALUES
(NULL, 7, 1, 325),
(NULL, 7, 2, 200);

-- Exact match: Pantocid DSR equivalent
INSERT INTO jan_aushadhi_composition VALUES
(NULL, 8, 12, 40),
(NULL, 8, 13, 30);

-- ==========================================================
-- DONE
-- ==========================================================
