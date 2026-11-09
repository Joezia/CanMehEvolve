
const FIT_UINT16 Profile::GetFieldIndex(const FIT_UINT16 mesgNum, const FIT_UINT8 fieldNum)
{
    const MESG *mesg = GetMesg(mesgNum);

    if (mesg == NULL)
        return FIT_UINT16_INVALID;

    // Binary search if fields are sorted by num (common in profile data)
    // Use lower_bound for O(log n) instead of O(n) linear scan
    auto it = std::lower_bound(mesg->fields, mesg->fields + mesg->numFields,
        fieldNum, [](const FIELD& a, FIT_UINT8 b) { return a.num < b; });

    if (it != mesg->fields + mesg->numFields && it->num == fieldNum)
        return static_cast<FIT_UINT16>(it - mesg->fields);

    return FIT_UINT16_INVALID;
}
