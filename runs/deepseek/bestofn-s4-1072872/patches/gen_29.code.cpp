FIT_UINT8 Field::GetNum(void) const
{
    auto p = profile;
    if (__builtin_expect(p == NULL, 0))
        return FIT_FIELD_NUM_INVALID;
    if (__builtin_expect(profileIndex >= p->numFields, 0))
        return FIT_FIELD_NUM_INVALID;
    return p->fields[profileIndex].num;
}
