
```cpp
const FIT_UINT16 Profile::GetFieldIndex(const FIT_UINT16 mesgNum, const FIT_UINT8 fieldNum)
{
    const MESG *mesg = GetMesg(mesgNum);

    if (mesg == NULL)
        return FIT_UINT16_INVALID;

    // Binary search since fields are guaranteed to be sorted by num (per SDK design)
    const FIELD *first = mesg->fields;
    const FIELD *last = mesg->fields + mesg->numFields;

    const FIELD *it = std::lower_bound(first, last, fieldNum,
        [](const FIELD& field, FIT_UINT8 num) { return field.num < num; });

    if (it != last && it->num == fieldNum)
        return static_cast<FIT_UINT16>(it - first);

    return FIT_UINT16_INVALID;
}
