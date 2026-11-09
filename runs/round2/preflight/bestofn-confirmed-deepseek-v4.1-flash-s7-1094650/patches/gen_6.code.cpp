FIT_UINT16 CRC::Get16(FIT_UINT16 crc, FIT_UINT8 byte)
{
   struct Table { FIT_UINT16 v[256]; };
   static constexpr Table crc_table = [] {
      Table t{};
      for (unsigned i = 0; i < 256; ++i)
      {
         FIT_UINT16 c = static_cast<FIT_UINT16>(i);
         for (int j = 0; j < 8; ++j)
         {
            c = (c & 1)
               ? static_cast<FIT_UINT16>((c >> 1) ^ 0xA001)
               : static_cast<FIT_UINT16>(c >> 1);
         }
         t.v[i] = c;
      }
      return t;
   }();

   return static_cast<FIT_UINT16>((crc >> 8) ^ crc_table.v[(crc ^ byte) & 0xFF]);
}
