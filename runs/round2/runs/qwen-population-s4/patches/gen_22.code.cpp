
FIT_FLOAT64 Field::GetOffset() const
{
    return (profile && profileIndex < profile->numFields)
        ? profile->fields[profileIndex].offset
        : 0.0;
}
