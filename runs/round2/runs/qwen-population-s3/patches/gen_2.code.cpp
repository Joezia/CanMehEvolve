
FIT_UINT16 CRC::Get16(FIT_UINT16 crc, FIT_UINT8 byte)
{
   static const FIT_UINT16 crc_table[16] =
   {
      0x0000, 0xCC01, 0xD801, 0x1400, 0xF001, 0x3C00, 0x2800, 0xE401,
      0xA001, 0x6C00, 0x7800, 0xB401, 0x5000, 0x9C01, 0x8801, 0x4400
   };

   // Process lower 4 bits
   FIT_UINT16 crc_low = crc_table[crc & 0xF];
   crc = ((crc >> 4) ^ crc_low) & 0x0FFF;

   // Process upper 4 bits
   crc = crc ^ crc_table[(crc & 0xF) ^ (byte & 0xF)];
   crc = ((crc >> 4) ^ crc_table[((crc >> 4) & 0xF) ^ ((byte >> 4) & 0xF)]) & 0x0FFF;

   return crc;
}
