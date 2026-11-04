FIT_UINT16 Field::GetNumSubFields(void) const
{
    const auto* p = profile;
    if (__builtin_expect(p == NULL, 0))
        return 0;

    const auto index = profileIndex;
    if (__builtin_expect(index >= p->numFields, 0))
        return 0;

    return p->fields[index].numSubFields;
}
