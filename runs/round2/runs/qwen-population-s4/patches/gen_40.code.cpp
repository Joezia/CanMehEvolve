FIT_UINT16 CRC::Get16(FIT_UINT16 crc, FIT_UINT8 byte)
{
   static const FIT_UINT16 crc_table[16] =
   {
      0x0000, 0xCC01, 0xD801, 0x1400, 0xF001, 0x3C00, 0x2800, 0xE401,
      0xA001, 0x6C00, 0x7800, 0xB401, 0x5000, 0x9C01, 0x8801, 0x4400
   };

   // Optimized version using branchless operations and reducing memory accesses
   FIT_UINT16 lo = crc_table[crc & 0xF];
   FIT_UINT16 hi = crc_table[(crc >> 4) & 0xF];
   crc = (crc >> 8) ^ lo ^ crc_table[byte & 0xF];
   crc = (crc >> 4) ^ hi ^ crc_table[(byte >> 4) & 0xF];

   return crc & 0x0FFF;
}
