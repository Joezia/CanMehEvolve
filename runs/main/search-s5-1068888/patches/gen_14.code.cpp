
    void SetEndTimezoneOffset(FIT_SINT16 endTimezoneOffset)
    {
        // Inline the call to avoid function call overhead for a simple field assignment
        // assuming FIT_SINT16 is a signed 16-bit type and field index 3 is static
        fields[3].value.i16 = endTimezoneOffset;
        fields[3].isValid = 1;
    }
