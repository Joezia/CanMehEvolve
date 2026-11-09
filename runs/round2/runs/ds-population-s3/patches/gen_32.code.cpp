FIT_FLOAT64 Field::GetScale() const
{
    const auto* p = profile;
    if (__builtin_expect(p == NULL, 0))
        return 1.0;
    if (__builtin_expect(profileIndex >= p->numFields, 0))
        return 1.0;
    return p->fields[profileIndex].scale;
}
