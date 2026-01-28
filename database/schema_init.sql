-- ==========================================================
-- RxLens : Extended Schema Initialization
-- Purpose: Support refined CSV ingestion + matching logic
-- DB: MySQL
-- ==========================================================

DROP DATABASE IF EXISTS rxlens;
CREATE DATABASE rxlens;
USE rxlens;

-- ----------------------------------------------------------
-- TABLE: drugs
-- ----------------------------------------------------------
CREATE TABLE drugs (
    drug_id INT AUTO_INCREMENT PRIMARY KEY,
    drug_name VARCHAR(150) NOT NULL UNIQUE
);

-- ----------------------------------------------------------
-- TABLE: brand_medicines
-- ----------------------------------------------------------
CREATE TABLE brand_medicines (
    medicine_id INT AUTO_INCREMENT PRIMARY KEY,
    brand_name VARCHAR(100) NOT NULL,
    medicine_name VARCHAR(300) NOT NULL
);

-- ----------------------------------------------------------
-- TABLE: brand_medicine_composition
-- ----------------------------------------------------------
CREATE TABLE brand_medicine_composition (
    id INT AUTO_INCREMENT PRIMARY KEY,
    medicine_id INT NOT NULL,
    drug_id INT NOT NULL,
    amount VARCHAR(50) NOT NULL,
    unit VARCHAR(50) NOT NULL,

    CONSTRAINT fk_brand_medicine
        FOREIGN KEY (medicine_id)
        REFERENCES brand_medicines(medicine_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_brand_drug
        FOREIGN KEY (drug_id)
        REFERENCES drugs(drug_id),

    CONSTRAINT uq_brand_medicine_drug
        UNIQUE (medicine_id, drug_id)
);

-- ----------------------------------------------------------
-- TABLE: jan_aushadhi_medicines
-- ----------------------------------------------------------
CREATE TABLE jan_aushadhi_medicines (
    medicine_id INT AUTO_INCREMENT PRIMARY KEY,
    medicine_name VARCHAR(300) NOT NULL,
    unit_size VARCHAR(150),
    mrp DECIMAL(8,2),
    group_name VARCHAR(200),
    category VARCHAR(50)
);

-- ----------------------------------------------------------
-- TABLE: jan_aushadhi_composition
-- ----------------------------------------------------------
CREATE TABLE jan_aushadhi_composition (
    id INT AUTO_INCREMENT PRIMARY KEY,
    medicine_id INT NOT NULL,
    drug_id INT NOT NULL,
    amount VARCHAR(50) NOT NULL,
    unit VARCHAR(50) NOT NULL,

    CONSTRAINT fk_jan_medicine
        FOREIGN KEY (medicine_id)
        REFERENCES jan_aushadhi_medicines(medicine_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_jan_drug
        FOREIGN KEY (drug_id)
        REFERENCES drugs(drug_id),

    CONSTRAINT uq_jan_medicine_drug
        UNIQUE (medicine_id, drug_id)
);
