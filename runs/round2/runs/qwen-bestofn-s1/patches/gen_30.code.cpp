
DeveloperFieldDefinition::DeveloperFieldDefinition(const DeveloperFieldDefinition& other)
    : num( other.num )
    , size( other.size )
    , developerDataIndex( other.developerDataIndex )
    , mesg( other.mesg ? new FieldDescriptionMesg(*other.mesg) : nullptr )
    , developer( other.developer ? new DeveloperDataIdMesg(*other.developer) : nullptr )
{
}
