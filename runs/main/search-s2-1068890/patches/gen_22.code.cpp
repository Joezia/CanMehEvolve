
const FIT_UINT16 Profile::GetFieldIndex(const FIT_UINT16 mesgNum, const FIT_UINT8 fieldNum)
{
    const MESG *mesg = GetMesg(mesgNum);

    if (mesg == NULL)
        return FIT_UINT16_INVALID;

    // Binary search over sorted fields array
    const FIT_FIELD *begin = mesg->fields;
    const FIT_FIELD *end = mesg->fields + mesg->numFields;
    
    auto it = std::lower_bound(begin, end, fieldNum,
        [](const FIT_FIELD& field, FIT_UINT8 num) { return field.num < num; });
    
    if (it != end && it->num == fieldNum)
        return static_cast<FIT_UINT16>(it - begin);
    
    return FIT_UINT16_INVALID;
}
