ALTER TABLE applications
ADD COLUMN compose_file TEXT;

ALTER TABLE applications
ADD COLUMN docker_network TEXT;

ALTER TABLE applications
ADD COLUMN status TEXT;
