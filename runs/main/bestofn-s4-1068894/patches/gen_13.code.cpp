
const FIT_UINT16 Profile::GetFieldIndex(const FIT_UINT16 mesgNum, const FIT_UINT8 fieldNum)
{
    const MESG *mesg = GetMesg(mesgNum);

    if (mesg == NULL)
        return FIT_UINT16_INVALID;

    // Binary search assuming fields are sorted by num (common in profile implementations)
    // Use lower_bound on the fields array's num field
    const FIELD *begin = mesg->fields;
    const FIELD *end = mesg->fields + mesg->numFields;
    const FIELD target = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}; // zero-initialize; only .num matters
    const FIELD key = {fieldNum, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}; // only .num set

    const FIELD* it = std::lower_bound(begin, end, key,
        [](const FIELD& a, const FIELD& b) { return a.num < b.num; });

    if (it != end && it->num == fieldNum)
        return static_cast<FIT_UINT16>(it - begin);

    return FIT_UINT16_INVALID;
}
