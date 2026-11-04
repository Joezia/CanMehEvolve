template <typename STRING_TYPE_DST, typename CHAR_TYPE_DST, typename STRING_TYPE_SRC, typename CHAR_TYPE_SRC>
FIT_BOOL ConvertStringEncoding(STRING_TYPE_DST& strDst, const FIT_UNICODE_ENCODING dstEncoding, const STRING_TYPE_SRC& strSrc, const FIT_UNICODE_ENCODING srcEncoding)
{
   STRING_TYPE_DST convertedStr;

   // If either encoding is undefined, the original implementation skips every
   // character and returns an empty string.
   if ((srcEncoding != FIT_UNICODE_ENCODING_UTF8 && srcEncoding != FIT_UNICODE_ENCODING_UTF16 && srcEncoding != FIT_UNICODE_ENCODING_UTF32) ||
       (dstEncoding != FIT_UNICODE_ENCODING_UTF8 && dstEncoding != FIT_UNICODE_ENCODING_UTF16 && dstEncoding != FIT_UNICODE_ENCODING_UTF32))
   {
      strDst = convertedStr;
      return FIT_TRUE;
   }

   convertedStr.reserve(strSrc.size());

   const unsigned long int srcSize = static_cast<unsigned long int>(strSrc.size());

   for (unsigned long int i = 0; i < srcSize; ++i)
   {
      // Fast path for ASCII code points.  All supported encodings encode
      // U+0000..U+007F as a single unit with the same value.
      if (static_cast<unsigned long int>(strSrc[i]) < 0x80)
      {
         convertedStr.push_back((CHAR_TYPE_DST) strSrc[i]);
         continue;
      }

      FIT_LARGE_TYPE codePoint = 0;
      bool valid = true;

      // Decode the source.
      switch (srcEncoding)
      {
         case FIT_UNICODE_ENCODING_UTF8:
         {
            if (!UTF8_IS_UNIT_VALID(strSrc[i]))
            {
               valid = false;
               break;
            }

            unsigned long int numUnits = 0;
            if (UTF8_IS_UNIT_1UNIT(strSrc[i]))
               numUnits = 1;
            else if (UTF8_IS_UNIT_2UNIT_LEAD(strSrc[i]))
               numUnits = 2;
            else if (UTF8_IS_UNIT_3UNIT_LEAD(strSrc[i]))
               numUnits = 3;
            else if (UTF8_IS_UNIT_4UNIT_LEAD(strSrc[i]))
               numUnits = 4;
            else
            {
               valid = false;
               break;
            }

            unsigned long int numContUnits = numUnits - 1;
            while (numContUnits--)
            {
               if ((++i) >= srcSize)
               {
                  valid = false;
                  break;
               }
               if (!UTF8_IS_UNIT_MULTI_CONT(strSrc[i]))
               {
                  valid = false;
                  break;
               }
               if (!UTF8_IS_UNIT_VALID(strSrc[i]))
               {
                  valid = false;
                  break;
               }
            }

            if (!valid)
               break;

            switch (numUnits)
            {
               case 1:
                  codePoint = UTF8_1UNIT_TO_POINT(strSrc[i]);
                  if (!UTF8_IS_POINT_1UNIT(codePoint))
                     valid = false;
                  break;
               case 2:
                  codePoint = UTF8_2UNIT_TO_POINT(strSrc[i - 1], strSrc[i]);
                  if (!UTF8_IS_POINT_2UNIT(codePoint))
                     valid = false;
                  break;
               case 3:
                  codePoint = UTF8_3UNIT_TO_POINT(strSrc[i - 2], strSrc[i - 1], strSrc[i]);
                  if (!UTF8_IS_POINT_3UNIT(codePoint))
                     valid = false;
                  break;
               case 4:
                  codePoint = UTF8_4UNIT_TO_POINT(strSrc[i - 3], strSrc[i - 2], strSrc[i - 1], strSrc[i]);
                  if (!UTF8_IS_POINT_4UNIT(codePoint))
                     valid = false;
                  break;
            }
            break;
         }

         case FIT_UNICODE_ENCODING_UTF16:
         {
            if (!UTF16_IS_UNIT_VALID(strSrc[i]))
            {
               valid = false;
               break;
            }

            if (UTF16_IS_UNIT_1UNIT(strSrc[i]))
            {
               codePoint = static_cast<FIT_LARGE_TYPE>(UTF16_1UNIT_TO_POINT(strSrc[i]));
               if (!UTF16_IS_POINT_1UNIT(codePoint))
                  valid = false;
            }
            else if (UTF16_IS_UNIT_2UNIT_LEAD(strSrc[i]))
            {
               if ((++i) >= srcSize)
               {
                  valid = false;
                  break;
               }
               if (!UTF16_IS_UNIT_2UNIT_TAIL(strSrc[i]))
               {
                  valid = false;
                  break;
               }
               if (!UTF16_IS_UNIT_VALID(strSrc[i]))
               {
                  valid = false;
                  break;
               }
               codePoint = static_cast<FIT_LARGE_TYPE>(UTF16_2UNIT_TO_POINT(strSrc[i - 1], strSrc[i]));
               if (!UTF16_IS_POINT_2UNIT(codePoint))
                  valid = false;
            }
            else
            {
               valid = false;
            }
            break;
         }

         case FIT_UNICODE_ENCODING_UTF32:
         {
            if (!UTF32_IS_UNIT_VALID(strSrc[i]))
            {
               valid = false;
               break;
            }
            codePoint = static_cast<FIT_LARGE_TYPE>(UTF32_UNIT_TO_POINT(strSrc[i]));
            break;
         }
      }

      if (!valid)
         continue;

      // Check that the code point is valid.
      if (!UNICODE_IS_POINT_VALID(codePoint))
         continue;

      // Encode the destination.
      switch (dstEncoding)
      {
         case FIT_UNICODE_ENCODING_UTF8:
            if (UTF8_IS_POINT_1UNIT(codePoint))
            {
               convertedStr.push_back((CHAR_TYPE_DST) UTF8_POINT_TO_1UNIT(codePoint));
            }
            else if (UTF8_IS_POINT_2UNIT(codePoint))
            {
               convertedStr.push_back((CHAR_TYPE_DST) UTF8_POINT_TO_2UNIT_LEAD(codePoint));
               convertedStr.push_back((CHAR_TYPE_DST) UTF8_POINT_TO_2UNIT_CONT1(codePoint));
            }
            else if (UTF8_IS_POINT_3UNIT(codePoint))
            {
               convertedStr.push_back((CHAR_TYPE_DST) UTF8_POINT_TO_3UNIT_LEAD(codePoint));
               convertedStr.push_back((CHAR_TYPE_DST) UTF8_POINT_TO_3UNIT_CONT1(codePoint));
               convertedStr.push_back((CHAR_TYPE_DST) UTF8_POINT_TO_3UNIT_CONT2(codePoint));
            }
            else if (UTF8_IS_POINT_4UNIT(codePoint))
            {
               convertedStr.push_back((CHAR_TYPE_DST) UTF8_POINT_TO_4UNIT_LEAD(codePoint));
               convertedStr.push_back((CHAR_TYPE_DST) UTF8_POINT_TO_4UNIT_CONT1(codePoint));
               convertedStr.push_back((CHAR_TYPE_DST) UTF8_POINT_TO_4UNIT_CONT2(codePoint));
               convertedStr.push_back((CHAR_TYPE_DST) UTF8_POINT_TO_4UNIT_CONT3(codePoint));
            }
            break;

         case FIT_UNICODE_ENCODING_UTF16:
            if (UTF16_IS_POINT_1UNIT(codePoint))
            {
               convertedStr.push_back((CHAR_TYPE_DST) UTF16_POINT_TO_1UNIT(codePoint));
            }
            else if (UTF16_IS_POINT_2UNIT(codePoint))
            {
               convertedStr.push_back((CHAR_TYPE_DST) UTF16_POINT_TO_2UNIT_LEAD(codePoint));
               convertedStr.push_back((CHAR_TYPE_DST) UTF16_POINT_TO_2UNIT_TAIL(codePoint));
            }
            break;

         case FIT_UNICODE_ENCODING_UTF32:
            convertedStr.push_back((CHAR_TYPE_DST) UTF32_POINT_TO_UNIT(codePoint));
            break;
      }
   }

   strDst = convertedStr;
   return FIT_TRUE;
}
