info_count = 4
error_count = 5
warning_count = 8

# Using f-strings with format specifiers
info_msg = f"INFO - {info_count:>3}"
error_msg = f"ERROR - {error_count:>3}"
warning_msg = f"WARNING - {warning_count:>3}"

print(info_msg)
print(error_msg)
print(warning_msg)
