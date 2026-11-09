
const FIT_UINT16 Profile::GetFieldIndex(const FIT_UINT16 mesgNum, const FIT_UINT8 fieldNum)
{
    const MESG *mesg = GetMesg(mesgNum);

    if (mesg == NULL || mesg->numFields == 0)
        return FIT_UINT16_INVALID;

    const FIELD *fields = mesg->fields;
    
    // Early exit for out-of-bounds field numbers (profile fields are sorted)
    if (fieldNum < fields[0].num || fieldNum > fields[mesg->numFields - 1].num)
        return FIT_UINT16_INVALID;

    // Binary search for O(log n) lookup instead of O(n) linear search
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
