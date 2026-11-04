FIT_UINT16 CRC::Get16(FIT_UINT16 crc, FIT_UINT8 byte)
{
   static constexpr std::array<FIT_UINT16, 256> crc_table = []() constexpr {
      std::array<FIT_UINT16, 256> table{};
      for (int i = 0; i < 256; ++i)
      {
         FIT_UINT16 c = static_cast<FIT_UINT16>(i);
         for (int j = 0; j < 8; ++j)
         {
            c = (c & 1) ? static_cast<FIT_UINT16>((c >> 1) ^ 0xA001)
                        : static_cast<FIT_UINT16>(c >> 1);
         }
         table[i] = c;
      }
      return table;
   }();

   return static_cast<FIT_UINT16>((crc >> 8) ^ crc_table[(crc ^ byte) & 0xFF]);
}
