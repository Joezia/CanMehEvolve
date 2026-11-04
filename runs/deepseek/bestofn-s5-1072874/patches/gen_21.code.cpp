FIT_UINT8 Field::GetNum(void) const
{
    const auto* p = profile;
    if (__builtin_expect(p == nullptr, 0))
        return FIT_FIELD_NUM_INVALID;

    const FIT_UINT8 idx = profileIndex;
    if (__builtin_expect(idx >= p->numFields, 0))
        return FIT_FIELD_NUM_INVALID;

    return p->fields[idx].num;
}
