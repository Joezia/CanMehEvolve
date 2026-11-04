
```cpp
const FIT_UINT16 Profile::GetFieldIndex(const FIT_UINT16 mesgNum, const FIT_UINT8 fieldNum)
{
    const MESG *mesg = GetMesg(mesgNum);

    if (mesg == NULL)
        return FIT_UINT16_INVALID;

    // Use binary search if fields are sorted (profile guarantees this)
    const FieldDef *begin = mesg->fields;
    const FieldDef *end = begin + mesg->numFields;
    auto it = std::lower_bound(begin, end, fieldNum,
        [](const FieldDef& def, FIT_UINT8 num) { return def.num < num; });

    if (it != end && it->num == fieldNum)
        return static_cast<FIT_UINT16>(std::distance(begin, it));

    return FIT_UINT16_INVALID;
}
