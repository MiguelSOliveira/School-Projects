require 'csv'

$Data = CSV.read('weather.csv')
$Data = CSV.read('iris2.csv')
$Data = CSV.read('restaurant.csv')

# Create attributes and branches variables
attributes = []
branches = {}
$Data[0].each do |column|
  attributes.push column
  branches[column] = []
end
branches.delete(attributes[0])
branches.delete(attributes[-1])
attributes = attributes[1..-2]

#Create solutions
solutions = {}
$Data[1..-1].each do |line|
  if not solutions[line[-1]]
    solutions[line[-1]] = []
  end
end

# Generate nodes of each branch
(1..$Data[0].size-2).each do |column|
  $Data[0..-1].each do |line|
    if line[column] != [] and not branches[$Data[0][column]].include? line[column]
      branches[$Data[0][column]].push line[column]
    end
  end
  branches[$Data[0][column]].delete($Data[0][column])
end

def AllEquals examples
  lastIndex = examples[0].size-1
  compareVar = examples[0][lastIndex]
  examples.each do |example|
    if example[lastIndex] != compareVar
      return false
    end
  end
  return true
end

def checkMajorAttribute examples
  majorAtts = {}
  maxAttribute = ""
  maxValue = 0
  examples.each do |example|
    majorAtts[example[-1]] = 0 if not majorAtts[example[-1]]
    majorAtts[example[-1]] += 1
  end
  majorAtts.each do |key,value|
    if value > maxValue
      maxValue = value
      maxAttribute = key
    end
  end
  return maxAttribute, (maxValue/examples.size.to_f).round(2), maxValue
end

$tree = {}
def CreateTree attributes, examples, solutions, branches
  if AllEquals examples
    lastIndex = examples[0].size-1
    return examples[0][lastIndex], examples.size, examples.size
  else
    best = ChooseAttribute attributes, examples, solutions
    if best != ""
      $tree[best] = []
      branches[best].each do |branch|
        $tree[best].push branch
      end
      branches[best].each do |vi|
        $tree[vi] = []
        examplesSubset = []
        examples.each do |example|
          if example.include? vi
            examplesSubset.push example
          end
        end
        if examplesSubset.empty?
          $tree[vi].push checkMajorAttribute examples
        else
          $tree[vi].push CreateTree attributes-[best],examplesSubset, solutions, branches
        end
      end
    end
  end
end

def ChooseAttribute attributes, examples, solutions
  maxGain = 0
  maxAttribute = ""
  solutionsTemp = {}
  (1..examples[0].size).each do |column|
    solutions.each do |key,value|
      solutionsTemp[key] = [] if not solutionsTemp[key]
      solutionsTemp[key].push value
    end
    totalGain = 0
    branches = {}
    examples.each do |elem|
      if not branches[elem[column]]
        branches[elem[column]] = [elem[0]]
      else
        branches[elem[column]].push elem[0]
      end
      solutionsTemp[elem[-1]].push elem[0] if solutionsTemp[elem[-1]] != nil
    end
    totalExamples = examples.size
    branches.each do |branch|
      solutionsTemp.each do |solution|
        intersection = branch[1] & solution[1]
        const = branch[1].size / totalExamples.to_f
        logConst = intersection.size / branch[1].size.to_f
        log = Math::log(logConst, 2)
        log = 0 if log.infinite?
        totalGain += const * (-logConst * log)
      end
    end
    if maxGain < (1-totalGain)
      maxGain = (1-totalGain)
      maxAttribute = attributes[column-1][0..-1] if attributes[column-1]
    end
  end
  return maxAttribute
end

def evaluateNewCase newCase, root, solutions
  while true
    branches = $tree[root]
    branches = branches.flatten
    intersection = newCase & branches
    intersection = intersection[0]
    if intersection == nil
      return "#{branches[0]} - #{((branches[1]/$tree[intersection][2].to_f)*100).round(2)}%"
    elsif solutions.include? $tree[intersection][0]
      return "#{$tree[intersection][0]} - #{(($tree[intersection][1]/$tree[intersection][2].to_f)*100).round(2)}%"
    end
    root = intersection
  end
end

def printTree root, solutions, spaces
  spaces += "   "
  return if not $tree[root]
  $tree[root].each do |branch|
    if not $tree[branch]
      print "  #{branch} #{$tree[root][1]}" if not branch.is_a?(Float) and not branch.is_a?(Integer)
    end
    if not branch.is_a?(Integer) and $tree[branch]
      print "\n" + spaces + "#{branch}:"
    end
    printTree branch, solutions, spaces
  end
end

root = ChooseAttribute attributes, $Data[1..-1], solutions
CreateTree attributes, $Data[1..-1], solutions, branches

# Flatten tree e.g [[1,2,3]] = [1,2,3]
$tree.each do |branch|
  $tree[branch[0]] = $tree[branch[0]].flatten
end

puts "\nFile Inputs"
File.open("examplesTesting", "r").each_line do |ex|
  puts evaluateNewCase ex.split(","), root, solutions
end
puts

print "Decision Tree"
printTree root, solutions, ""
puts
