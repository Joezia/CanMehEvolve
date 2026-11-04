FIT_BOOL DeveloperFieldDefinition::IsDefined() const
{
    return static_cast<FIT_BOOL>((nullptr != mesg) & (nullptr != developer));
}
