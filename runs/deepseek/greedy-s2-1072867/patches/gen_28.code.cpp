FIT_UINT8 Field::GetNum(void) const
{
    const auto p = profile;
    const auto idx = profileIndex;
    if (__builtin_expect(p == NULL, 0))
        return FIT_FIELD_NUM_INVALID;
    return p->fields[idx].num;
}
