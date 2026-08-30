data "aws_availability_zones" "available" {
  state = "available"
}

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "${var.service_name}-vpc-${var.env}"
    Service     = var.service_name
    Environment = var.env
    ManagedBy   = "tradeforge"
  }
}

resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index)
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name      = "${var.service_name}-private-${count.index}-${var.env}"
    Tier      = "private"
    ManagedBy = "tradeforge"
  }
}

# NO public subnets — banking-grade default
# All outbound traffic via NAT Gateway only

resource "aws_eip" "nat" {
  domain = "vpc"
}

resource "aws_nat_gateway" "main" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.private[0].id
}