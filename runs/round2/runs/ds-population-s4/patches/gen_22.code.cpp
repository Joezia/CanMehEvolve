FIT_UINT16 Field::GetNumComponents(void) const
{
    const auto* p = profile;
    const auto idx = profileIndex;
    if (__builtin_expect(p == NULL, 0))
        return 0;
    if (__builtin_expect(idx >= p->numFields, 0))
        return 0;
    return p->fields[idx].numComponents;
}
