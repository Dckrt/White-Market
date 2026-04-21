-- ============================================================
-- WHITE MARKET — Complete Oracle Schema (Updated with Price History + Tags)
-- Run this in SQL Developer with F5
-- ============================================================

-- STEP 1: Drop tables
BEGIN
  FOR t IN (
    SELECT table_name FROM user_tables
    WHERE table_name IN ('PRICE_HISTORY','NOTIFICATIONS','MESSAGES','CART','PRODUCTS','USERS')
  ) LOOP
    EXECUTE IMMEDIATE 'DROP TABLE ' || t.table_name || ' CASCADE CONSTRAINTS PURGE';
  END LOOP;
END;
/

-- STEP 2: Drop sequences
BEGIN
  FOR s IN (
    SELECT sequence_name FROM user_sequences
    WHERE sequence_name IN ('USERS_SEQ','PRODUCTS_SEQ','CART_SEQ','MESSAGES_SEQ','NOTIF_SEQ','PRICE_HIST_SEQ')
  ) LOOP
    EXECUTE IMMEDIATE 'DROP SEQUENCE ' || s.sequence_name;
  END LOOP;
END;
/

-- STEP 3: Create sequences
CREATE SEQUENCE users_seq       START WITH 1 INCREMENT BY 1 NOCACHE NOCYCLE;
CREATE SEQUENCE products_seq    START WITH 1 INCREMENT BY 1 NOCACHE NOCYCLE;
CREATE SEQUENCE cart_seq        START WITH 1 INCREMENT BY 1 NOCACHE NOCYCLE;
CREATE SEQUENCE messages_seq    START WITH 1 INCREMENT BY 1 NOCACHE NOCYCLE;
CREATE SEQUENCE notif_seq       START WITH 1 INCREMENT BY 1 NOCACHE NOCYCLE;
CREATE SEQUENCE price_hist_seq  START WITH 1 INCREMENT BY 1 NOCACHE NOCYCLE;

-- STEP 4: Create tables

-- USERS
CREATE TABLE USERS (
  id                NUMBER         PRIMARY KEY,
  name              VARCHAR2(100)  NOT NULL,
  email             VARCHAR2(150)  NOT NULL UNIQUE,
  password_hash     VARCHAR2(255)  NOT NULL,
  student_id_number VARCHAR2(50),
  course            VARCHAR2(200),
  year_level        VARCHAR2(20),
  department        VARCHAR2(200),
  profile_pic       VARCHAR2(500),
  gcash_number      VARCHAR2(20),
  bank_details      VARCHAR2(200),
  created_at        DATE           DEFAULT SYSDATE
);

-- PRODUCTS (with tags and multi-image support)
CREATE TABLE PRODUCTS (
  id          NUMBER          PRIMARY KEY,
  title       VARCHAR2(200)   NOT NULL,
  description VARCHAR2(2000),
  price       NUMBER(10, 2)   NOT NULL,
  category    VARCHAR2(100)   DEFAULT 'General',
  status      VARCHAR2(50)    DEFAULT 'Available',
  seller_id   NUMBER          REFERENCES USERS(id) ON DELETE CASCADE,
  image_url   CLOB,            -- stores JSON array of image URLs
  tags        VARCHAR2(500),   -- comma-separated tags e.g. "calculator,scientific,casio"
  created_at  DATE            DEFAULT SYSDATE
);

-- PRICE_HISTORY (tracks price changes over time)
CREATE TABLE PRICE_HISTORY (
  id          NUMBER        PRIMARY KEY,
  product_id  NUMBER        REFERENCES PRODUCTS(id) ON DELETE CASCADE,
  price       NUMBER(10, 2) NOT NULL,
  recorded_at DATE          DEFAULT SYSDATE
);

-- CART
CREATE TABLE CART (
  id         NUMBER  PRIMARY KEY,
  user_id    NUMBER  REFERENCES USERS(id)    ON DELETE CASCADE,
  product_id NUMBER  REFERENCES PRODUCTS(id) ON DELETE CASCADE,
  quantity   NUMBER  DEFAULT 1,
  added_at   DATE    DEFAULT SYSDATE,
  CONSTRAINT cart_unique UNIQUE (user_id, product_id)
);

-- MESSAGES
CREATE TABLE MESSAGES (
  id          NUMBER          PRIMARY KEY,
  sender_id   NUMBER          REFERENCES USERS(id)    ON DELETE CASCADE,
  receiver_id NUMBER          REFERENCES USERS(id)    ON DELETE CASCADE,
  product_id  NUMBER          REFERENCES PRODUCTS(id) ON DELETE SET NULL,
  message     VARCHAR2(4000)  NOT NULL,
  sent_at     DATE            DEFAULT SYSDATE,
  is_read     NUMBER(1)       DEFAULT 0
);

-- NOTIFICATIONS
CREATE TABLE NOTIFICATIONS (
  id         NUMBER         PRIMARY KEY,
  user_id    NUMBER         REFERENCES USERS(id) ON DELETE CASCADE,
  message    VARCHAR2(500)  NOT NULL,
  is_read    NUMBER(1)      DEFAULT 0,
  created_at DATE           DEFAULT SYSDATE
);

-- STEP 5: Indexes
CREATE INDEX idx_products_seller   ON PRODUCTS(seller_id);
CREATE INDEX idx_products_status   ON PRODUCTS(status);
CREATE INDEX idx_products_category ON PRODUCTS(category);
CREATE INDEX idx_price_hist_prod   ON PRICE_HISTORY(product_id);
CREATE INDEX idx_cart_user         ON CART(user_id);
CREATE INDEX idx_msg_sender        ON MESSAGES(sender_id);
CREATE INDEX idx_msg_receiver      ON MESSAGES(receiver_id);
CREATE INDEX idx_notif_user        ON NOTIFICATIONS(user_id);

-- STEP 6: Verify
SELECT 'USERS'         AS tbl, COUNT(*) AS cnt FROM USERS         UNION ALL
SELECT 'PRODUCTS'      AS tbl, COUNT(*) AS cnt FROM PRODUCTS      UNION ALL
SELECT 'PRICE_HISTORY' AS tbl, COUNT(*) AS cnt FROM PRICE_HISTORY UNION ALL
SELECT 'CART'          AS tbl, COUNT(*) AS cnt FROM CART          UNION ALL
SELECT 'MESSAGES'      AS tbl, COUNT(*) AS cnt FROM MESSAGES      UNION ALL
SELECT 'NOTIFICATIONS' AS tbl, COUNT(*) AS cnt FROM NOTIFICATIONS;

SELECT 'White Market schema created successfully!' AS status FROM DUAL;