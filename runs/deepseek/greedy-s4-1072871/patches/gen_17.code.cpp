FIT_BOOL DeveloperFieldDefinition::IsDefined() const
{
    return static_cast<FIT_BOOL>((mesg != nullptr) & (developer != nullptr));
}
