
```cpp
const FIT_UINT16 Profile::GetFieldIndex(const FIT_UINT16 mesgNum, const FIT_UINT8 fieldNum)
{
    const MESG *mesg = GetMesg(mesgNum);

    if (mesg == NULL)
        return FIT_UINT16_INVALID;

    // Use binary search since fields are sorted by num (as per FIT spec)
    const Field *begin = mesg->fields;
    const Field *end = mesg->fields + mesg->numFields;

    const Field key = { fieldNum, 0, 0, 0, 0 };
    const Field *it = std::lower_bound(begin, end, key,
        [](const Field& a, const Field& b) { return a.num < b.num; });

    if (it != end && it->num == fieldNum)
        return static_cast<FIT_UINT16>(it - begin);

    return FIT_UINT16_INVALID;
}
