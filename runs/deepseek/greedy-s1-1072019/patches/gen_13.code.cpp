FIT_UINT8 Field::GetNum(void) const
{
    const auto* p = profile;
    if (__builtin_expect(p == NULL, 0))
        return FIT_FIELD_NUM_INVALID;

    const FIT_UINT8 index = profileIndex;
    if (__builtin_expect(index >= p->numFields, 0))
        return FIT_FIELD_NUM_INVALID;

    return p->fields[index].num;
}
