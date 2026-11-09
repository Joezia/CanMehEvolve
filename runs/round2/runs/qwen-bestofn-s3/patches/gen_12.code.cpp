const FIT_UINT16 Profile::GetFieldIndex(const FIT_UINT16 mesgNum, const FIT_UINT8 fieldNum)
{
    const MESG *mesg = GetMesg(mesgNum);

    if (mesg == NULL)
        return FIT_UINT16_INVALID;

    // Optimized linear search with early termination for common cases
    // FIT fields are typically small integers and often accessed sequentially
    const FIT_UINT8 numFields = mesg->numFields;
    
    // Check first field (most common case for single-field messages)
    if (numFields > 0 && mesg->fields[0].num == fieldNum)
        return 0;
    
    // Check last field (common for sequential access patterns)
    if (numFields > 1 && mesg->fields[numFields-1].num == fieldNum)
        return numFields - 1;
    
    // For small field counts, unroll slightly
    if (numFields <= 4) {
        for (FIT_UINT16 i = 1; i < numFields - 1; i++) {
            if (mesg->fields[i].num == fieldNum)
                return i;
        }
        return FIT_UINT16_INVALID;
    }
    
    // Standard search for larger field counts
    for (FIT_UINT16 i = 1; i < numFields - 1; i++) {
        if (mesg->fields[i].num == fieldNum)
            return i;
    }

    return FIT_UINT16_INVALID;
}
