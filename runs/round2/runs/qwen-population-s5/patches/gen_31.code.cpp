
```cpp
const FIT_UINT16 Profile::GetFieldIndex(const FIT_UINT16 mesgNum, const FIT_UINT8 fieldNum)
{
    const MESG *mesg = GetMesg(mesgNum);

    if (mesg == NULL)
        return FIT_UINT16_INVALID;

    // Use binary search if fields are sorted (common in profile data)
    // Linear search fallback if unsorted, but we assume sorted for speed
    // Check first and last for quick early exit
    if (mesg->numFields == 0)
        return FIT_UINT16_INVALID;
    
    const FIELD *fields = mesg->fields;
    
    // Quick checks for min/max field numbers to skip binary search in common cases
    if (fieldNum < fields[0].num || fieldNum > fields[mesg->numFields - 1].num)
        return FIT_UINT16_INVALID;

    // Binary search since FIT profile fields are typically sorted by field number
    FIT_UINT16 left = 0;
    FIT_UINT16 right = mesg->numFields - 1;

    while (left <= right) {
        FIT_UINT16 mid = (left + right) >> 1;
        FIT_UINT8 midNum = fields[mid].num;

        if (midNum == fieldNum) {
            return mid;
        } else if (midNum < fieldNum) {
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }

    return FIT_UINT16_INVALID;
}
