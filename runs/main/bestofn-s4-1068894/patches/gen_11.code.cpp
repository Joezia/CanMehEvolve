
FIT_UINT16 CRC::Get16(FIT_UINT16 crc, FIT_UINT8 byte)
{
   static const FIT_UINT16 crc_table[16] =
   {
      0x0000, 0xCC01, 0xD801, 0x1400, 0xF001, 0x3C00, 0x2800, 0xE401,
      0xA001, 0x6C00, 0x7800, 0xB401, 0x5000, 0x9C01, 0x8801, 0x4400
   };

   // Process both nibbles in one expression to reduce branches and temporaries
   FIT_UINT16 n0 = crc & 0xF;
   FIT_UINT16 n1 = (crc >> 4) & 0xF;
   FIT_UINT16 n2 = (byte & 0xF);
   FIT_UINT16 n3 = (byte >> 4) & 0xF;

   crc = ((crc >> 8) ^ crc_table[n0] ^ crc_table[n2]) ^ (crc_table[n1] ^ crc_table[n3]);

   return crc;
}
