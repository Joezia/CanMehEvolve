FIT_UINT8 Field::GetNum(void) const
{
    const auto index = profileIndex;
    const auto* p = profile;
    if (__builtin_expect(p == NULL, 0))
        return FIT_FIELD_NUM_INVALID;
    const auto numFields = p->numFields;
    const auto* fields = p->fields;
    if (__builtin_expect(index >= numFields, 0))
        return FIT_FIELD_NUM_INVALID;
    return fields[index].num;
}
