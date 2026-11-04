FIT_UINT16 Field::GetNumSubFields(void) const
{
    const auto* p = profile;
    if (__builtin_expect(p == NULL, 0))
        return 0;
    if (__builtin_expect(profileIndex >= p->numFields, 0))
        return 0;
    return p->fields[profileIndex].numSubFields;
}
