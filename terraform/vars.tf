# region vars
variable "region" {
  type = string
  default = "westeurope"
}

# network vars
variable "first_ip" {
  type = number
  default = 10
}


# credentials vars
variable "username" {
  type = string
  default = "admin"
}

variable "password" {
  type = string
  default = "@._admin4dm1n$"
}

# resources vars
variable "virtual_machine" {
  type = string
  default = "vm"
}

variable "k8s_master" {
  type = string
  default = "k8s_master"
}

variable "k8s_worker" {
  type = string
  default = "k8s_worker"
}

variable "nfs" {
  type = string
  default = "nfs"
}

variable "osdisk" {
  type = string
  default = "osdisk"
}

variable "stdisk" {
  type = string
  default = "stdisk"
}

variable "public_ip" {
  type = string
  default = "public_ip"
}

variable "nic" {
  type = string
  default = "nic"
}

variable "ipconf" {
  type = string
  default = "ipconf"
}