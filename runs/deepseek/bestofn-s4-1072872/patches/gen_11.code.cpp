FIT_UINT16 CRC::Get16(FIT_UINT16 crc, FIT_UINT8 byte)
{
   static constexpr std::array<FIT_UINT16, 256> crc_table = []() constexpr {
      constexpr FIT_UINT16 nibble_table[16] =
      {
         0x0000, 0xCC01, 0xD801, 0x1400, 0xF001, 0x3C00, 0x2800, 0xE401,
         0xA001, 0x6C00, 0x7800, 0xB401, 0x5000, 0x9C01, 0x8801, 0x4400
      };

      std::array<FIT_UINT16, 256> table{};
      for (unsigned int i = 0; i < 256; ++i)
      {
         const FIT_UINT8 b = static_cast<FIT_UINT8>(i);
         FIT_UINT16 c = 0;
         FIT_UINT16 tmp = nibble_table[c & 0xF];
         c = static_cast<FIT_UINT16>((c >> 4) & 0x0FFF);
         c = static_cast<FIT_UINT16>(c ^ tmp ^ nibble_table[b & 0xF]);

         tmp = nibble_table[c & 0xF];
         c = static_cast<FIT_UINT16>((c >> 4) & 0x0FFF);
         c = static_cast<FIT_UINT16>(c ^ tmp ^ nibble_table[(b >> 4) & 0xF]);

         table[i] = c;
      }
      return table;
   }();

   return static_cast<FIT_UINT16>((crc >> 8) ^ crc_table[(crc ^ byte) & 0xFF]);
}
