CREATE TABLE property (
    property_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255),
    address VARCHAR(255),
    bedroom_count INT,
    bathroom_count INT,
    price_per_night DECIMAL(10, 2),
    max_guests INT,
    cleaning_fee DECIMAL(10, 2),
    average_rating DECIMAL(5, 2),
    total_ratings INT
);

CREATE TABLE category (
    category_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255)
);

CREATE TABLE property_category (
    property_id VARCHAR(255),
    category_id VARCHAR(255),
    PRIMARY KEY (property_id, category_id),
    FOREIGN KEY (property_id) REFERENCES property(property_id),
    FOREIGN KEY (category_id) REFERENCES category(category_id)
);

CREATE TABLE bedroom (
    bedroom_id VARCHAR(255) PRIMARY KEY,
    property_id VARCHAR(255),
    bed_count INT,
    bed_type VARCHAR(255),
    FOREIGN KEY (property_id) REFERENCES property(property_id)
);

CREATE TABLE house_rule (
    house_rule_id VARCHAR(255) PRIMARY KEY,
    property_id VARCHAR(255),
    rule VARCHAR(255),
    FOREIGN KEY (property_id) REFERENCES property(property_id)
);

CREATE TABLE amenity (
    amenity_id VARCHAR(255) PRIMARY KEY,
    property_id VARCHAR(255),
    name VARCHAR(255),
    FOREIGN KEY (property_id) REFERENCES property(property_id)
);

CREATE TABLE photo (
    photo_id VARCHAR(255) PRIMARY KEY,
    property_id VARCHAR(255),
    url VARCHAR(255),
    FOREIGN KEY (property_id) REFERENCES property(property_id)
);

CREATE TABLE cancellation_policy (
    property_id VARCHAR(255) PRIMARY KEY,
    refundable BOOLEAN,
    refund_percentage DECIMAL(5, 2),
    refund_time_period VARCHAR(255),
    FOREIGN KEY (property_id) REFERENCES property(property_id)
);

CREATE TABLE user (
    user_id VARCHAR(255) PRIMARY KEY,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    date_of_birth DATE,
    address VARCHAR(255),
    gender VARCHAR(255),
    phone_number VARCHAR(255),
    email_address VARCHAR(255),
    password VARCHAR(255),
    profile_picture_url VARCHAR(255)
);

CREATE TABLE emergency_contact (
    user_id VARCHAR(255),
    name VARCHAR(255),
    relationship VARCHAR(255),
    preferred_language VARCHAR(255),
    email_address VARCHAR(255),
    country_code VARCHAR(255),
    phone_number VARCHAR(255),
    PRIMARY KEY (user_id, email_address),
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);

CREATE TABLE host (
    user_id VARCHAR(255) PRIMARY KEY,
    is_super_host BOOLEAN,
    host_rating DECIMAL(5, 2),
    total_host_ratings INT,
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);

CREATE TABLE guest (
    user_id VARCHAR(255) PRIMARY KEY,
    guest_rating DECIMAL(5, 2),
    total_guest_ratings INT,
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);

CREATE TABLE wishlist (
    wishlist_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255),
    name VARCHAR(255),
    privacy VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);

CREATE TABLE wishlist_property (
    wishlist_id VARCHAR(255),
    property_id VARCHAR(255),
    PRIMARY KEY (wishlist_id, property_id),
    FOREIGN KEY (wishlist_id) REFERENCES wishlist(wishlist_id),
    FOREIGN KEY (property_id) REFERENCES property(property_id)
);

CREATE TABLE booking (
    booking_id VARCHAR(255) PRIMARY KEY,
    guest_id VARCHAR(255),
    property_id VARCHAR(255),
    booking_date DATETIME,
    check_in_date DATETIME,
    check_out_date DATETIME,
    num_guests INT,
    modified_date DATETIME,
    tax_paid DECIMAL(10, 2),
    total_price DECIMAL(10, 2),
    total_price_with_taxes DECIMAL(10, 2),
    amount_paid DECIMAL(10, 2),
    amount_due DECIMAL(10, 2),
    promo_code VARCHAR(255),
    discount_amount DECIMAL(10, 2),
    is_cancelled BOOLEAN,
    cancellation_date DATETIME,
    refund_amount DECIMAL(10, 2),
    refund_paid DECIMAL(10, 2),
    FOREIGN KEY (guest_id) REFERENCES guest(user_id),
    FOREIGN KEY (property_id) REFERENCES property(property_id)
);

CREATE TABLE credit_card (
    card_number VARCHAR(255) PRIMARY KEY,
    guest_id VARCHAR(255),
    csv_number VARCHAR(255),
    expiration_date DATE,
    cardholder_name VARCHAR(255),
    card_type VARCHAR(255),
    billing_address VARCHAR(255),
    FOREIGN KEY (guest_id) REFERENCES guest(user_id)
);

CREATE TABLE bank_account (
    account_number VARCHAR(255) PRIMARY KEY,
    host_id VARCHAR(255),
    routing_number VARCHAR(255),
    account_type VARCHAR(255),
    FOREIGN KEY (host_id) REFERENCES host(user_id)
);

CREATE TABLE message (
    message_id VARCHAR(255) PRIMARY KEY,
    sender_id VARCHAR(255),
    receiver_id VARCHAR(255),
    date_created DATETIME,
    body TEXT,
    FOREIGN KEY (sender_id) REFERENCES user(user_id),
    FOREIGN KEY (receiver_id) REFERENCES user(user_id)
);

CREATE TABLE review (
    review_id VARCHAR(255) PRIMARY KEY,
    guest_id VARCHAR(255),
    host_id VARCHAR(255),
    property_id VARCHAR(255),
    booking_id VARCHAR(255),
    cleanliness_rating DECIMAL(5, 2),
    communication_rating DECIMAL(5, 2),
    check_in_rating DECIMAL(5, 2),
    accuracy_rating DECIMAL(5, 2),
    location_rating DECIMAL(5, 2),
    value_rating DECIMAL(5, 2),
    overall_rating DECIMAL(5, 2),
    comment TEXT,
    date_created DATETIME,
    date_modified DATETIME,
    FOREIGN KEY (guest_id) REFERENCES guest(user_id),
    FOREIGN KEY (host_id) REFERENCES host(user_id),
    FOREIGN KEY (property_id) REFERENCES property(property_id),
    FOREIGN KEY (booking_id) REFERENCES booking(booking_id)
);

