
FIT_FLOAT64 Field::GetScale() const
{
    if (!profile || profileIndex >= profile->numFields)
        return 1;
    return profile->fields[profileIndex].scale;
}
