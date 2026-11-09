
const FIT_UINT16 Profile::GetFieldIndex(const FIT_UINT16 mesgNum, const FIT_UINT8 fieldNum)
{
    const MESG *mesg = GetMesg(mesgNum);

    if (mesg == NULL)
        return FIT_UINT16_INVALID;

    // Binary search for sorted fields (profile data is sorted by field number)
    FIT_UINT16 left = 0;
    FIT_UINT16 right = mesg->numFields;
    
    while (left < right) {
        FIT_UINT16 mid = left + ((right - left) >> 1);
        if (mesg->fields[mid].num < fieldNum) {
            left = mid + 1;
        } else {
            right = mid;
        }
    }
    
    if (left < mesg->numFields && mesg->fields[left].num == fieldNum)
        return left;
    
    return FIT_UINT16_INVALID;
}
