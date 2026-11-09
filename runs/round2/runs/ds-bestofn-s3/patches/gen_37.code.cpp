FIT_UINT16 Field::GetNumSubFields(void) const
{
    auto* const p = profile;
    const FIT_UINT16 idx = profileIndex;
    if (__builtin_expect((p != nullptr) && (idx < p->numFields), 1))
        return p->fields[idx].numSubFields;
    return 0;
}
