FIT_BOOL Field::GetIsAccumulated() const
{
    const Profile::Field* fields = profile->fields;
    return fields[profileIndex].isAccumulated;
}
