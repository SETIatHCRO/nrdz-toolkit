USE nrdz;

INSERT INTO hardware
(
	id,
	location,
	hostname,
	nfs_mnt,
	wr_mac,
	rpi_mac,
	wr_ip,
	rpi_ip,
	usrp_sn
)
VALUES
(
	'hns-001',
	'HCRO-NRDZ-ROOFTOP',
	'hcro-rpi-001',
	'10.10.1.143:/mnt/datab on /mnt/datab-netStorage-1G',
	'N/A',
	'dc:a6:32:ec:f8:d0',
	'N/A',
	'10.1.42.17',
	'3227508'
),
(
	'hns-002',
	'HCRO-NRDZ-GATE',
	'hcro-rpi-002',
	'10.10.1.143:/mnt/datab on /mnt/datab-netStorage-1G',
	'08:00:30:71:34:6c',
	'dc:a6:32:ef:58:30',
	'10.1.42.100',
	'10.1.42.18',
	'323E367'
),
(
	'hns-003',
	'HCRO-NRDZ-CHIME',
	'hcro-rpi-003',
	'10.10.1.143:/mnt/datab on /mnt/datab-netStorage-1G',
	'08:00:30:70:d8:3c',
	'dc:a6:32:8f:c5:b4',
	'10.1.42.101',
	'10.1.42.19',
	'3227512'
),
(
	'hns-004',
	'HCRO-NRDZ-WEST-740',
	'hcro-rpi-004',
	'10.10.1.143:/mnt/datab on /mnt/datab-netStorage-1G',
	'08:00:30:71:34:63',
	'dc:a6:32:8f:a3:a6',
	'10.1.42.102',
	'10.1.42.20',
	'323E369'
),
(
	'hns-005',
	'HCRO-NRDZ-NORTH-1740',
	'hcro-rpi-005',
	'10.10.1.143:/mnt/datab on /mnt/datab-netStorage-1G',
	'08:00:30:81:28:c4',
	'dc:a6:32:ec:f9:b2',
	'10.1.42.103',
	'10.1.42.21',
	'32274A4'
);
