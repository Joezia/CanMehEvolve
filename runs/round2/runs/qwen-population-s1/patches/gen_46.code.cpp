
FIT_UINT16 CRC::Get16(FIT_UINT16 crc, FIT_UINT8 byte)
{
   static const FIT_UINT16 crc_table[16] =
   {
      0x0000, 0xCC01, 0xD801, 0x1400, 0xF001, 0x3C00, 0x2800, 0xE401,
      0xA001, 0x6C00, 0x7800, 0xB401, 0x5000, 0x9C01, 0x8801, 0x4400
   };

   // Combine both nibble operations using a lookup table approach
   FIT_UINT16 tmp = crc_table[(crc ^ byte) & 0x0F];
   crc = (crc >> 4) ^ tmp;
   tmp = crc_table[(crc ^ (byte >> 4)) & 0x0F];
   crc = (crc >> 4) ^ tmp;

   return crc;
}
