FIT_UINT16 Field::GetNumComponents(void) const
{
    const auto* p = profile;
    if (__builtin_expect(p != NULL && profileIndex < p->numFields, 1))
        return p->fields[profileIndex].numComponents;
    return 0;
}
